from flask import Flask, request, render_template_string
from collections import OrderedDict
import ast

app = Flask(__name__)

def merge_inputs(input1, input2):
    # Create a copy of input1
    result = input1.copy()
    
    # Process each entry in input2
    for tokens2, value2 in input2.items():
        tokens2 = tuple([tokens2] if isinstance(tokens2, str) else tokens2)  # Ensure single tokens are tuples
        token_set2 = set(tokens2)
        
        # Remove any input1 tuples with overlapping tokens
        for tokens1 in list(result.keys()):
            tokens1 = tuple([tokens1] if isinstance(tokens1, str) else tokens1)
            if token_set2 & set(tokens1):  # Check for any intersection
                del result[tokens1]
        
        # Merge with input1 tuple having the same value, if available
        merged = False
        for tokens1, value1 in list(result.items()):
            tokens1 = tuple([tokens1] if isinstance(tokens1, str) else tokens1)
            if value1 == value2 and not merged:
                new_tokens = tuple(sorted(set(tokens1) | token_set2))  # Merge tokens, sort
                del result[tokens1]  # Remove old tuple
                result[new_tokens] = value2
                merged = True
                break
        
        # If no merge occurred, add the input2 tuple
        if not merged:
            result[tokens2] = value2

    # Ensure all keys are tuples
    final_result = OrderedDict()
    for k, v in result.items():
        k = tuple([k] if isinstance(k, str) else k)
        final_result[k] = v

    # Sort by value
    sorted_result = OrderedDict(sorted(final_result.items(), key=lambda x: x[1]))
    return sorted_result

# HTML template with input fields, submit button, result display, and copy button
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Merge Inputs</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        textarea { width: 100%; height: 200px; margin-bottom: 10px; font-family: monospace; }
        button { padding: 10px 20px; margin-right: 10px; }
        #result { border: 1px solid #ccc; padding: 10px; white-space: pre-wrap; font-family: monospace; }
        .error { color: red; }
    </style>
</head>
<body>
    <h2>Merge Input Dictionaries</h2>
    <form method="POST" action="/">
        <label for="input1">Input 1 (Python dict format):</label><br>
        <textarea id="input1" name="input1" placeholder="{
    ('AA', 'BB'): 1,
    ('CC'): 2,
    ('DD'): 3
}"></textarea><br>
        <label for="input2">Input 2 (Python dict format):</label><br>
        <textarea id="input2" name="input2" placeholder="{
    ('CC'): 1,
    ('AA'): 3
}"></textarea><br>
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
            # Parse input as Python dictionaries using ast.literal_eval
            input1_str = request.form.get('input1')
            input2_str = request.form.get('input2')
            input1 = ast.literal_eval(input1_str)
            input2 = ast.literal_eval(input2_str)
            
            # Ensure keys are tuples
            input1 = {tuple([k] if isinstance(k, str) else k): v for k, v in input1.items()}
            input2 = {tuple([k] if isinstance(k, str) else k): v for k, v in input2.items()}
            
            # Merge inputs
            merged = merge_inputs(input1, input2)
            
            # Format result as Python dictionary string
            result_lines = ["{"]
            for tokens, value in merged.items():
                result_lines.append(f"    {tokens}: {value},")
            result_lines[-1] = result_lines[-1].rstrip(",")  # Remove trailing comma
            result_lines.append("}")
            result = "\n".join(result_lines)
        except Exception as e:
            error = f"Error: {str(e)}. Please ensure inputs are valid Python dictionaries with tuple or string keys."
    
    return render_template_string(HTML_TEMPLATE, result=result, error=error)

if __name__ == '__main__':
    app.run(debug=True)
