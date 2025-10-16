from flask import Flask, request, render_template_string
from collections import OrderedDict
import json

app = Flask(__name__)

def merge_inputs(input1, input2):
    # Create a copy of input1
    result = input1.copy()
    
    # Update or add entries from input2
    for tokens, value in input2.items():
        token_set = set(tokens)
        for existing_tokens in list(result.keys()):
            if set(existing_tokens) == token_set:
                del result[existing_tokens]
        result[tokens] = value

    # Sort by value
    sorted_result = OrderedDict(sorted(result.items(), key=lambda x: x[1]))
    return sorted_result

# HTML template with input fields, submit button, result display, and copy button
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Merge Inputs</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        textarea { width: 100%; height: 200px; margin-bottom: 10px; }
        button { padding: 10px 20px; margin-right: 10px; }
        #result { border: 1px solid #ccc; padding: 10px; white-space: pre-wrap; }
        .error { color: red; }
    </style>
</head>
<body>
    <h2>Merge Input Dictionaries</h2>
    <form method="POST" action="/">
        <label for="input1">Input 1 (JSON format):</label><br>
        <textarea id="input1" name="input1" placeholder='{
    "[\"PENGU\", \"WLFI\", \"ZRO\", \"ASTER\", \"FXS\", \"HOME\", \"OKB\", \"NEWT\", \"ENA\", \"FLOW\"]": 1.0,
    "[\"DOGE\", \"TRX\", \"XRP\", \"SOL\"]": 0.01
}'></textarea><br>
        <label for="input2">Input 2 (JSON format):</label><br>
        <textarea id="input2" name="input2" placeholder='{
    "[\"BAT\", \"BRETT\", \"ORDER\", \"PENDLE\", \"WAL\"]": 1.0,
    "[\"THETA\"]": 0.6
}'></textarea><br>
        <button type="submit">Submit</button>
    </form>
    {% if result %}
        <h3>Result:</h3>
        <div id="result">{{ result }}</div>
        <button onclick="copyResult()">Copy Result</button>
    {% endif %}
    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}
    <script>
        function copyResult() {
            const result = document.getElementById('result').innerText;
            navigator.clipboard.writeText(result).then(() => {
                alert('Result copied to clipboard!');
            }).catch(err => {
                alert('Failed to copy: ' + err);
            });
        }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        try:
            # Parse input JSON
            input1_str = request.form.get('input1')
            input2_str = request.form.get('input2')
            input1 = {tuple(json.loads(k)): v for k, v in json.loads(input1_str).items()}
            input2 = {tuple(json.loads(k)): v for k, v in json.loads(input2_str).items()}
            
            # Merge inputs
            merged = merge_inputs(input1, input2)
            
            # Format result as JSON string for display
            result_json = {json.dumps(list(k)): v for k, v in merged.items()}
            result = json.dumps(result_json, indent=4)
        except Exception as e:
            error = f"Error: {str(e)}. Please ensure inputs are valid JSON."
    
    return render_template_string(HTML_TEMPLATE, result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)
