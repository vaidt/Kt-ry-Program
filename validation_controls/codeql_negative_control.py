"""ASIG validation-only negative control. DO NOT MERGE.

This fixture intentionally models an unsafe remote-input-to-eval flow solely
for validating native CodeQL merge protection. It is not production code.
"""
from flask import Flask, request

app = Flask(__name__)


@app.get("/_asig_validation_only/eval")
def unsafe_eval():
    expression = request.args.get("expression", "")
    return str(eval(expression))  # Intentionally vulnerable validation fixture.
