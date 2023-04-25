import aiohttp
import asyncio
from dataclasses import dataclass, field
from typing import Literal
import os

URL = "https://www.quora.com/poe_api/gql_POST"
HEADERS = {
    'Host': 'www.quora.com',
    'Accept': '*/*',
    'apollographql-client-version': '1.1.6-65',
    'Accept-Language': 'en-US,en;q=0.9',
    'User-Agent': 'Poe 1.1.6 rv:65 env:prod (iPhone14,2; iOS 16.2; en_US)',
    'apollographql-client-name': 'com.quora.app.Experts-apollo-ios',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
}

MODELS = Literal["capabara", "beaver", "a2_2", "a2", "chinchilla", "nutria"]


@dataclass
class PoeModel:
    model_name: MODELS
    def __str__(self):
        return self.model_name



@dataclass
class QuoraAuth:
    formkey: str
    cookie: str
    proxies: dict = None
    headers: dict = None

    def __post_init__(self):
        self.headers = HEADERS.copy()
        if not self.cookie.startswith("m-b="):
            self.cookie = f"m-b={self.cookie}"
        self.headers["Cookie"] = self.cookie
        self.headers["Quora-Formkey"] = self.formkey

    def __str__(self):
        return f"QuoraAuth(formkey={self.formkey}, cookie={self.cookie})"

    def __call__(self):
        if self.headers is None:
            self.__post_init__()
        return self.headers


@dataclass
class ChatSession:
    model: PoeModel
    auth: QuoraAuth
    chat_id: str = ""
    history: list[dict] = field(default_factory=list)
    last_message: dict = field(default_factory=dict)
    session: aiohttp.ClientSession = None

    @classmethod
    async def create(cls, model: PoeModel, auth: QuoraAuth):
        self = cls(model, auth)
        if auth.proxies:
            assert "http" in auth.proxies and "https" in auth.proxies, "Proxies must contain both http and https"
            os.environ["HTTP_PROXY"] = auth.proxies["http"]
            os.environ["HTTPS_PROXY"] = auth.proxies["https"]

        self.session = aiohttp.ClientSession(headers=auth(), trust_env=bool(auth.proxies))


        data = {
            'operationName': 'ChatViewQuery',
            'query': 'query ChatViewQuery($bot: String!) {\n  chatOfBot(bot: $bot) {\n    __typename\n    ...ChatFragment\n  }\n}\nfragment ChatFragment on Chat {\n  __typename\n  id\n  chatId\n  defaultBotNickname\n  shouldShowDisclaimer\n}',
            'variables': {
                'bot': self.model.model_name
            }
        }   

        async with self.session.post(URL, json=data) as resp:
            self.chat_id = (await resp.json())["data"]["chatOfBot"]["chatId"]

        return self

    async def send_message(self, message: str):
        data = {
            "operationName": "AddHumanMessageMutation",
            "query": "mutation AddHumanMessageMutation($chatId: BigInt!, $bot: String!, $query: String!, $source: MessageSource, $withChatBreak: Boolean! = false) {\n  messageCreate(\n    chatId: $chatId\n    bot: $bot\n    query: $query\n    source: $source\n    withChatBreak: $withChatBreak\n  ) {\n    __typename\n    message {\n      __typename\n      ...MessageFragment\n      chat {\n        __typename\n        id\n        shouldShowDisclaimer\n      }\n    }\n    chatBreak {\n      __typename\n      ...MessageFragment\n    }\n  }\n}\nfragment MessageFragment on Message {\n  id\n  __typename\n  messageId\n  text\n  linkifiedText\n  authorNickname\n  state\n  vote\n  voteReason\n  creationTime\n  suggestedReplies\n}",
            "variables": {
                "bot": self.model.model_name,
                "chatId": self.chat_id,
                "query": message,
                "source": None,
                "withChatBreak": False
            }
        }

        async with self.session.post(URL, json=data) as resp:
            return await self.retrieve_last_message()

    async def clear_context(self):
        data = {
            "operationName": "AddMessageBreakMutation",
            "query": "mutation AddMessageBreakMutation($chatId: BigInt!) {\n  messageBreakCreate(chatId: $chatId) {\n    __typename\n    message {\n      __typename\n      ...MessageFragment\n    }\n  }\n}\nfragment MessageFragment on Message {\n  id\n  __typename\n  messageId\n  text\n  linkifiedText\n  authorNickname\n  state\n  vote\n  voteReason\n  creationTime\n  suggestedReplies\n}",
            "variables": {
                "chatId": self.chat_id
            }
        }

        async with self.session.post(URL, json=data) as resp:
            return await resp.json()
    
    async def retrieve_last_message(self, stream: bool = False) -> dict:
        data = {
            "operationName": "ChatPaginationQuery",
            "query": "query ChatPaginationQuery($bot: String!, $before: String, $last: Int! = 10) {\n  chatOfBot(bot: $bot) {\n    id\n    __typename\n    messagesConnection(before: $before, last: $last) {\n      __typename\n      pageInfo {\n        __typename\n        hasPreviousPage\n      }\n      edges {\n        __typename\n        node {\n          __typename\n          ...MessageFragment\n        }\n      }\n    }\n  }\n}\nfragment MessageFragment on Message {\n  id\n  __typename\n  messageId\n  text\n  linkifiedText\n  authorNickname\n  state\n  vote\n  voteReason\n  creationTime\n}",
            "variables": {
                "before": None,
                "bot": self.model.model_name,
                "last": 1
            }
        } 

        while True:
            async with self.session.post(URL, json=data) as resp:
                response: dict = await resp.json()
                if response["data"]["chatOfBot"]["messagesConnection"]["edges"][-1]["node"]["state"] != "incomplete":
                    break
            await asyncio.sleep(1)
        
        self.last_message = response["data"]["chatOfBot"]["messagesConnection"]["edges"][-1]["node"]
        self.history.append(self.last_message)
        return self.last_message