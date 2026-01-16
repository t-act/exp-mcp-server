import asyncio
import json
import os
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from openai import OpenAI


async def main():
    # サーバープロセスを起動してstdio接続
    exp_code = "mcp_server_1"
    server_params = StdioServerParameters(
        command="/Users/tact/Dev/mcp-server-sample/.venv/bin/python",
        args=[f"/Users/tact/Dev/mcp-server-sample/{exp_code}.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # セッション初期化
            await session.initialize()
            
            # ツール一覧を取得
            tools = await session.list_tools()
            
            # OpenAI LLMでツール選択の実験
            print("\n" + "="*60)
            print("=== LLM Tool Selection Experiment ===")
            print("="*60)
            
            # OpenAI APIキーの確認
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("\n⚠️  OPENAI_API_KEYが設定されていません")
                print("\nLLM実験をスキップします。実験を行うには:")
                print("  export OPENAI_API_KEY='your-api-key'")
                print("を実行してから再度お試しください。")
                print("\n" + "="*60)
                return
            
            # MCPツールをOpenAI関数形式に変換
            openai_tools = []
            for tool in tools.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
            
            # OpenAI クライアント初期化
            client = OpenAI(api_key=api_key)
            
            # 実験1: 天気についての質問
            print("\n【実験1】天気についての質問")
            print("質問: 「東京の天気を教えて」")
            
            response1 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": "東京の天気を教えて"}
                ],
                tools=openai_tools,
                tool_choice="auto"
            )
            
            if response1.choices[0].message.tool_calls:
                tool_call = response1.choices[0].message.tool_calls[0]
                print(f"✅ LLMが選択したツール: {tool_call.function.name}")
                print(f"   引数: {tool_call.function.arguments}")
                
                # 実際にMCPツールを呼び出し
                args = json.loads(tool_call.function.arguments)
                result = await session.call_tool(tool_call.function.name, args)
                print(f"   結果: {result.content[0].text}")
            else:
                print("❌ ツールが呼び出されませんでした")
            
            # 実験2: 計算についての質問
            print("\n【実験2】計算についての質問")
            print("質問: 「100 + 200を計算して」")
            
            response2 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": "100 + 200を計算して"}
                ],
                tools=openai_tools,
                tool_choice="auto"
            )
            
            if response2.choices[0].message.tool_calls:
                tool_call = response2.choices[0].message.tool_calls[0]
                print(f"✅ LLMが選択したツール: {tool_call.function.name}")
                print(f"   引数: {tool_call.function.arguments}")
                
                # 実際にMCPツールを呼び出し
                args = json.loads(tool_call.function.arguments)
                result = await session.call_tool(tool_call.function.name, args)
                print(f"   結果: {result.content[0].text}")
            else:
                print("❌ ツールが呼び出されませんでした")
            
            # 実験3: 曖昧な質問
            print("\n【実験3】曖昧な質問")
            print("質問: 「東京について教えて」")
            
            response3 = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": "東京について教えて"}
                ],
                tools=openai_tools,
                tool_choice="auto"
            )
            
            if response3.choices[0].message.tool_calls:
                tool_call = response3.choices[0].message.tool_calls[0]
                print(f"✅ LLMが選択したツール: {tool_call.function.name}")
                print(f"   引数: {tool_call.function.arguments}")
            else:
                print("❌ ツールが呼び出されませんでした")
                print(f"   回答: {response3.choices[0].message.content}")
            

if __name__ == "__main__":
    asyncio.run(main())