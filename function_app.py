"""
This file is used by Azure functions to run the code. If you want to run
the code manually, use extract_article.py instead.
"""

import azure.functions as func

app = func.FunctionApp()

@app.function_name(name="HttpTrigger1")
@app.route(route="req")
def main(req):
    user = req.params.get("user")
    return f"Hello, {user}!"