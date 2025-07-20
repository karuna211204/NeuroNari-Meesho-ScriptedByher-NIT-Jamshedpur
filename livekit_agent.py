import logging
import asyncio
import os
from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import Agent, AgentSession, JobContext, JobRequest, WorkerOptions, cli, llm
from livekit.plugins.google.beta.realtime import RealtimeModel
from mcp_client import MCPServerSse
from fastmcp import Client

mcp = Client("http://127.0.0.1:8000/sse")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

# Validate Google API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")
logger.info("Google API key is configured")

# === Custom Agent Class ===
class MCPDemoAgent(Agent):
    def __init__(self, *, tools: list[llm.FunctionTool], mcp_server: MCPServerSse):
        super().__init__(
            instructions="""
Act like a multilingual, human-like AI health assistant working at a voice-powered clinic reception. You are integrated into an MCP server with access to three tools: `queue_appointment`, `send_appointment_sms`, and `generate_health_record`.

🎯 Your purpose is to help users — in any language — with their health-related concerns, hygiene questions, appointment bookings, health reports, and general advice. You must always reply in the same language the user speaks (e.g., Hindi, Telugu, English). Never switch languages mid-conversation.

Follow this step-by-step process for every interaction:

Step 1: Detect and use the user's spoken language for the entire conversation.
- If you cannot detect the language after initial speech, say: “I couldn't detect your language. Could you please tell me which language you'd like to continue in?”

Step 2: If the user shares health symptoms:
- Suggest a possible cause in friendly, everyday language.
- Add a short, gentle disclaimer: “This is general guidance, not a medical diagnosis.”
- Share a simple health precaution.
- Ask: “Would you like me to help you book a doctor’s appointment?”

Step 3: If the user agrees to schedule an appointment:
- Ask for and collect: name, age, gender, phone number, and reason for the appointment.
- Generate a unique patient ID automatically.
- If the user provides a specific time, use it. Otherwise, assign a random time.
- Confirm details: “Just confirming — your name is ___, you’re ___ years old, and you're booking for ___. Shall I go ahead?”
- Call `queue_appointment`. If successful, say: **“Appointment Booked.”**
- Internally remember all collected appointment details for future use (especially for generating health reports).

Step 4: After booking, ask: “Would you like to receive a confirmation SMS?”
- If yes, collect name and phone (reuse from earlier if available) and appointment time.
- Call `send_appointment_sms`. If successful, say: **“SMS Sent.”**

Step 5: Ask: “Would you like me to create a health report based on your symptoms?”
- If yes, reuse: name, age, gender, phone number, symptoms (from appointment data).
- Then ask for **missing health record details one by one**, in this order:
  1. Duration of symptoms
  2. Chronic or long-term health issues (e.g., diabetes, asthma)
  3. Hereditary or family medical history
  4. Any current medications or treatments
  5. Diagnosis (if shared)
  6. Prescriptions (if shared)
- After collecting all, call `generate_health_record`. If successful, say: **“Record Created.”**

Step 6: Maintain session memory — do not ask the user to repeat details already provided unless needed for clarification.

Step 7: If the user does not speak for 6 seconds:
- Say something like:
  - “I didn’t hear you — could you please say that again?”
  - “Take your time, I’m here when you’re ready.”
- Keep the session active unless the user explicitly ends it.

Step 8: If the user interrupts while you're speaking, stop and ask:
  - “Would you like me to continue or respond to your latest message instead?”

Step 9: If speech is unclear, say:
  - “Sorry, could you repeat that more clearly?”
  - Retry up to 2 times.

Step 10: If the user expresses gratitude or makes small talk:
  - Respond warmly: “You’re very welcome! I’m happy to assist.”

Step 11: Always end with a kind message:
  - “Get well soon!”
  - “Wishing you better health!”
  - “Let me know if you need anything else.”

Step 12: Do not ask for patient ID or appointment time — generate them unless the user specifies a time.

Take a deep breath and work on this problem step-by-step.


""",
            llm=RealtimeModel(
                voice="Aoede",
                temperature=0.8
            ),
            tools=tools,
            allow_interruptions=True
        )
        self._mcp = mcp_server

    async def on_user_turn(self, transcript: str, ctx: JobContext):
        logger.info(f"User said: {transcript}")
        return await super().on_user_turn(transcript, ctx)

    async def on_tool_call(self, tool_name: str, args: dict, ctx: JobContext):
        logger.info(f"Calling tool: {tool_name} with args: {args}")
        return await super().on_tool_call(tool_name, args, ctx)

# === Entry Point Function ===
async def entrypoint(ctx: JobContext):
    logger.info("Launching MCP Voice Health Agent...")

    mcp_server = MCPServerSse({"url": "http://127.0.0.1:8000/sse"})

    for attempt in range(3):
        try:
            await mcp_server.connect()
            logger.info("✅ MCP server connected")
            break
        except Exception as e:
            logger.warning(f"MCP connection failed (attempt {attempt + 1}): {e}")
            if attempt == 2:
                raise
            await asyncio.sleep(2)

    # ✅ Get tools from FastMCP server (no tool_impl)
    raw_tools = await mcp_server.get_agent_tools()
    logger.info(f"✅ Loaded raw tools: {[tool.__name__ for tool in raw_tools]}")

    tool_map = {tool.__name__: tool for tool in raw_tools}
    tools = []

    for tool_name in ["queue_appointment", "send_appointment_sms", "generate_health_record"]:
        tool = tool_map.get(tool_name)
        if tool:
            tools.append(tool)
            logger.info(f"✅ Loaded: {tool_name}")
        else:
            logger.warning(f"❌ Missing tool: {tool_name}")

    logger.info(f"🔧 Total tools passed to Agent: {len(tools)} → {[t.name for t in tools]}")

    agent = MCPDemoAgent(tools=tools, mcp_server=mcp_server)

    await ctx.connect()
    logger.info("Connected to LiveKit room")

    session = AgentSession()
    session.input.set_audio_enabled(True)
    session.output.set_audio_enabled(True)

    try:
        await session.start(agent=agent, room=ctx.room)
        logger.info("✅ Agent session started")
    except Exception as e:
        logger.error(f"❌ Agent session failed: {e}")
        raise

    room_io = session._room_io

    @ctx.room.local_participant.register_rpc_method("start_turn")
    async def start_turn(data: rtc.RpcInvocationData):
        logger.info(f"Start turn: {data.caller_identity}")
        session.interrupt()
        session.clear_user_turn()
        room_io.set_participant(data.caller_identity)
        session.input.set_audio_enabled(True)
        session.output.set_audio_enabled(True)

    @ctx.room.local_participant.register_rpc_method("end_turn")
    async def end_turn(data: rtc.RpcInvocationData):
        logger.info(f"End turn: {data.caller_identity}")
        session.commit_user_turn()

    @ctx.room.local_participant.register_rpc_method("cancel_turn")
    async def cancel_turn(data: rtc.RpcInvocationData):
        logger.info(f"Cancel turn: {data.caller_identity}")
        session.clear_user_turn()

    logger.info("🎙️ Voice Agent is ready.")

# === Handle Incoming Jobs ===
async def handle_request(request: JobRequest) -> None:
    logger.info(f"📨 Received job request: {request}")
    await request.accept(identity="multilingual-health-agent")

# === CLI Entrypoint ===
if __name__ == "__main__":
    logger.info("🔁 Starting LiveKit Health Voice Agent...")

    async def debug_tools():
        async with mcp:
            tools = await mcp.list_tools()
            for tool in tools:
                print(f"🧰 Available tool from MCP: {tool.name}")

    asyncio.run(debug_tools())

    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        request_fnc=handle_request
    ))
