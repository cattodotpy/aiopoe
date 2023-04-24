import poe
import asyncio

async def main():
    session = await poe.ChatSession.create(
        poe.PoeModel("chinchilla"), #ChatGPT
        poe.QuoraAuth(
            formkey="d3e1f2c854dafb4a866f40b0b6c68dca",
            cookie="5aeqtoI6cNV85S8EvB_08g=="
        )
    )

    while True:
        user = input("User: ")
        if user == "!end":
            break
        elif user == "!eoc":
            print("Clearing context...")
            await session.clear_context()
            print("👍")
            continue

        resp = await session.send_message(user)
        print("Bot: ", end="")
        print(
            resp.get("text", "No response")
        )


asyncio.run(main())
