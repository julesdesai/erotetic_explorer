import os
from flask import Flask, render_template, request, jsonify
import asyncio
import aiohttp
from openai import OpenAI
import json

app = Flask(__name__)

# Configuration constants
GPT_MODEL = "gpt-4o-mini"  # Can be changed to "gpt-4" or other models
MAX_ITEMS = 3  # Reduced from 5 to 3
API_KEY = os.getenv('OPENAI_API_KEY')
# Get API key from environment variable
client = OpenAI(api_key=API_KEY)


def debug_print(title, content):
    print(f"\n=== {title} ===")
    print(json.dumps(content, indent=2))
    print("================\n")

async def async_get_responses(question, mode):
    """Get initial responses to the central question"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": GPT_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that provides clear, concise responses."},
                        {"role": "user", "content": f"{'From a philosophical perspective, ' if mode == 'philosophical' else ''}Provide exactly {MAX_ITEMS} responses to: '{question}'. Each response should be on a new line starting with a dash (-)."}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            ) as response:
                result = await response.json()
                debug_print("API Response", result)
                
                content = result['choices'][0]['message']['content'].strip()
                responses = [r.strip('- ').strip() for r in content.split('\n') if r.strip()]
                
                # Ensure exactly MAX_ITEMS responses
                while len(responses) < MAX_ITEMS:
                    responses.append(f"Additional response to: {question}")
                
                return responses[:MAX_ITEMS]
    except Exception as e:
        print(f"Error in async_get_responses: {str(e)}")
        return [f"Error getting response {i+1}" for i in range(MAX_ITEMS)]

async def async_get_objections(response, mode):
    """Get objections to a given response"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": GPT_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that provides critical analysis."},
                        {"role": "user", "content": f"{'From a philosophical perspective, ' if mode == 'philosophical' else ''}Provide exactly {MAX_ITEMS} objections to: '{response}'. Each objection should be on a new line starting with a dash (-)."}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            ) as response:
                result = await response.json()
                content = result['choices'][0]['message']['content'].strip()
                objections = [r.strip('- ').strip() for r in content.split('\n') if r.strip()]
                
                while len(objections) < MAX_ITEMS:
                    objections.append(f"Additional objection to: {response}")
                
                return objections[:MAX_ITEMS]
    except Exception as e:
        print(f"Error in async_get_objections: {str(e)}")
        return [f"Error getting objection {i+1}" for i in range(MAX_ITEMS)]

async def async_get_counter_responses(objection, mode):
    """Get responses to objections"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": GPT_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that provides thoughtful responses."},
                        {"role": "user", "content": f"{'From a philosophical perspective, ' if mode == 'philosophical' else ''}Provide exactly {MAX_ITEMS} counter-arguments to: '{objection}'. Each counter-argument should be on a new line starting with a dash (-)."}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            ) as response:
                result = await response.json()
                content = result['choices'][0]['message']['content'].strip()
                responses = [r.strip('- ').strip() for r in content.split('\n') if r.strip()]
                
                while len(responses) < MAX_ITEMS:
                    responses.append(f"Additional counter to: {objection}")
                
                return responses[:MAX_ITEMS]
    except Exception as e:
        print(f"Error in async_get_counter_responses: {str(e)}")
        return [f"Error getting counter {i+1}" for i in range(MAX_ITEMS)]

async def generate_dialectical_tree(central_question, depth, mode):
    print(f"\nGenerating tree for question: {central_question}")
    print(f"Using model: {GPT_MODEL}")
    print(f"Depth: {depth}, Mode: {mode}, Items per level: {MAX_ITEMS}")
    
    nodes = [{"id": "C", "group": "question", "label": central_question, "level": 0, "display_id": "C"}]
    links = []
    
    async def process_level(parent_nodes, current_depth):
        if current_depth > depth * 2:
            return

        print(f"\nProcessing depth {current_depth} with {len(parent_nodes)} parent nodes")
        
        api_calls = []
        for parent in parent_nodes:
            if current_depth % 2 == 1:  # Odd levels are responses/counter-responses
                if current_depth == 1:
                    api_calls.append(async_get_responses(parent["label"], mode))
                else:
                    api_calls.append(async_get_counter_responses(parent["label"], mode))
            else:  # Even levels are objections
                api_calls.append(async_get_objections(parent["label"], mode))

        all_items = await asyncio.gather(*api_calls, return_exceptions=True)
        
        new_nodes = []
        for parent_idx, parent in enumerate(parent_nodes):
            items = all_items[parent_idx] if not isinstance(all_items[parent_idx], Exception) else [f"Error {i+1}" for i in range(MAX_ITEMS)]
            group = "answer" if current_depth % 2 == 1 else "question"
            
            for i, item in enumerate(items[:MAX_ITEMS]):
                if current_depth == 1:
                    display_id = f"R{i+1}"
                elif current_depth == 2:
                    display_id = f"R{parent['display_id'][1]}O{i+1}"
                else:
                    display_id = f"{parent['display_id']}{'R' if group == 'answer' else 'O'}{i+1}"
                
                node = {
                    "id": display_id,
                    "group": group,
                    "label": item,
                    "level": current_depth,
                    "display_id": display_id
                }
                nodes.append(node)
                new_nodes.append(node)
                links.append({"source": parent["id"], "target": display_id})
        
        if new_nodes:
            await process_level(new_nodes, current_depth + 1)
    
    await process_level([nodes[0]], 1)
    return nodes, links

@app.route('/')
def home():
    return render_template('index_dialectical_calder.html') #render_template('index_dialectical.html')

@app.route('/generate_questions', methods=['POST'])
def generate_questions_and_answers():
    try:
        data = request.json
        central_question = data['question']
        mode = data.get('mode', 'general')
        depth = data.get('depth', 2)

        nodes, links = asyncio.run(generate_dialectical_tree(
            central_question, depth, mode
        ))

        return jsonify({
            'nodes': nodes,
            'links': links
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Only use debug mode locally
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode)
