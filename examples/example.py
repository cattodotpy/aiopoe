import poe
import asyncio
import dotenv
import os

dotenv.load_dotenv()

async def main():
    session = await poe.ChatSession.create(
        poe.PoeModel("chinchilla"), #ChatGPT
        poe.QuoraAuth(
            formkey=os.getenv("FORMKEY"),
            cookie=os.getenv("COOKIE")
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
