# mcp_server.py
from mcp.server import FastMCP

server = FastMCP("tool-docstring-test")


@server.tool()
def alpha(x: str) -> str:
    """
    都市名を受け取り、その都市の天気を説明する。
    """
    return f"{x} の天気は晴れです"


@server.tool()
def beta(x: str) -> str:
    """
    文字列で与えられた数値を処理する。
    """
    return "計算結果です"


@server.tool()
def gamma(x: str) -> str:
    """
    都市名を受け取り、その都市の緯度と経度を返す。
    """
    return f"{x} の緯度はxx、経度はooです"

if __name__ == "__main__":
    # stdio モード（Claude Desktop等のMCPクライアント用）
    server.run()