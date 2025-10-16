from flask import Flask, request, jsonify
from collections import OrderedDict

app = Flask(__name__)

def merge_inputs(input1, input2):
    # Create a copy of input1 to avoid modifying the original
    result = input1.copy()
    
    # Update or add entries from input2
    for tokens, value in input2.items():
        # Convert tuple to set for comparison (order-independent)
        token_set = set(tokens)
        # Check if any tuple in result has the same tokens (ignoring order)
        for existing_tokens in list(result.keys()):
            if set(existing_tokens) == token_set:
                # Remove the old tuple if it matches
                del result[existing_tokens]
        # Add the new tuple and value
        result[tokens] = value

    # Sort the result by value
    sorted_result = OrderedDict(sorted(result.items(), key=lambda x: x[1]))
    return sorted_result

@app.route('/merge', methods=['POST'])
def merge_dictionaries():
    try:
        # Get JSON data from the request
        data = request.get_json()
        input1 = {tuple(k): v for k, v in data.get('input1', {}).items()}
        input2 = {tuple(k): v for k, v in data.get('input2', {}).items()}
        
        # Merge the inputs
        result = merge_inputs(input1, input2)
        
        # Convert tuples back to lists for JSON serialization
        result_json = {list(k): v for k, v in result.items()}
        
        return jsonify(result_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
