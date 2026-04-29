#!/usr/bin/env python3
"""Working browser-use with Ollama - no timeout version"""
import os
import sys

# Bypass proxy
os.environ['no_proxy'] = 'localhost,127.0.0.1,192.168.43.136'
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,192.168.43.136'

from browser_use.llm.openai.chat import ChatOpenAI
from browser_use.browser import BrowserProfile
from browser_use.agent.service import Agent
import asyncio

print("Setting up OpenAI-compatible LLM...")
llm = ChatOpenAI(
    model="qwen3.5:9b",
    api_key="ollama",
    base_url="http://192.168.43.136:8080/v1"
)

print("Creating browser profile...")
browser_profile = BrowserProfile(
    headless=False,
    args=['--no-proxy-server']
)

print("Creating agent...")
agent = Agent(
    task="Go to google.com and tell me the title",
    llm=llm,
    browser_profile=browser_profile
)

print("Running agent (no timeout)...")
asyncio.run(agent.run())
print("Done!")