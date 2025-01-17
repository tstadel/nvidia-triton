import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from tabulate import tabulate
import random
from transformers import AutoTokenizer
import tiktoken
import tritonclient.http as httpclient


# Specify the Triton server URL and model name
url = "localhost:8000"  # Adjust if Triton server is running on a different machine or port
model_name = "multilingual_e5_base"

passages_300 = [
"This is a passage on exercise which you need to follow. The importance of regular physical exercise cannot be overstated in maintaining overall health and well-being. Engaging in daily physical activities such as walking, jogging, swimming, or cycling promotes cardiovascular health, improves lung capacity, and enhances muscle strength. It also helps to regulate weight by burning excess calories and increases energy levels, making individuals feel more alert and productive. Furthermore, exercise stimulates the release of endorphins, the body's natural mood elevators, which reduce stress and anxiety levels. Studies have shown that regular exercise can reduce the risk of chronic diseases such as heart disease, diabetes, and hypertension. In addition to the physical benefits, exercise plays a significant role in improving mental health by boosting self-esteem, reducing symptoms of depression, and enhancing cognitive function. Exercising outdoors, in particular, can further improve mental well-being by allowing individuals to connect with nature, reduce feelings of isolation, and breathe fresh air. {action} is essential for maintaining {object}. Without proper {action}, you might experience {symptom}. Additionally, staying hydrated and consuming a balanced diet that supports your physical efforts will further enhance the effectiveness of your workout. Supplements like vitamins, minerals, and protein shakes can also support your body’s needs during periods of high physical exertion. Adequate rest and sleep are equally vital for recovery, allowing your muscles to heal and grow stronger over time. Regular exercise after certain age is very vital for muscles as it prevents the atrophy.",
"This is a passage on importance of exercise. The importance of regular physical exercise cannot be overstated in maintaining overall health and well-being. Engaging in daily physical activities such as walking, jogging, swimming, or cycling promotes cardiovascular health, improves lung capacity, and enhances muscle strength. It also helps to regulate weight by burning excess calories and increases energy levels, making individuals feel more alert and productive. Furthermore, exercise stimulates the release of endorphins, the body's natural mood elevators, which reduce stress and anxiety levels. Studies have shown that regular exercise can reduce the risk of chronic diseases such as heart disease, diabetes, and hypertension. In addition to the physical benefits, exercise plays a significant role in improving mental health by boosting self-esteem, reducing symptoms of depression, and enhancing cognitive function. Exercising outdoors, in particular, can further improve mental well-being by allowing individuals to connect with nature, reduce feelings of isolation, and breathe fresh air. Outdoor activities like hiking or biking provide both physical and mental stimulation, increasing your exposure to nature and natural sunlight, which boosts Vitamin D production. Additionally, group exercises, such as yoga classes or team sports, foster a sense of community and social interaction, which is critical in reducing feelings of loneliness and improving overall life satisfaction. The recommended amount of {entity} for {person} is around {amount}. This is based on the latest health guidelines, which suggest incorporating balance of aerobic and strength-training exercises to maximize health benefits. Execise is great." ,
"Do regular exercise when you are young. The importance of regular physical exercise cannot be overstated in maintaining overall health and well-being. Engaging in daily physical activities such as walking, jogging, swimming, or cycling promotes cardiovascular health, improves lung capacity, and enhances muscle strength. It also helps to regulate weight by burning excess calories and increases energy levels, making individuals feel more alert and productive. Furthermore, exercise stimulates the release of endorphins, the body's natural mood elevators, which reduce stress and anxiety levels. Studies have shown that regular exercise can reduce the risk of chronic diseases such as heart disease, diabetes, and hypertension. In addition to the physical benefits, exercise plays a significant role in improving mental health by boosting self-esteem, reducing symptoms of depression, and enhancing cognitive function. Exercising outdoors, in particular, can further improve mental well-being by allowing individuals to connect with nature, reduce feelings of isolation, and breathe fresh air. {action} is essential for maintaining {object}. Without proper {action}, you might experience {symptom}. Additionally, staying hydrated and consuming a balanced diet that supports your physical efforts will further enhance the effectiveness of your workout. Supplements like vitamins, minerals, and protein shakes can also support your body’s needs during periods of high physical exertion. Adequate rest and sleep are equally vital for recovery, allowing your muscles to heal and grow stronger over time. The exercise should also help one from recovering from surgery. It also prevents ageing and increase blood supply.",
"The importance of regular physical exercise cannot be overstated in maintaining overall health and well-being. Engaging in daily physical activities such as walking, jogging, swimming, or cycling promotes cardiovascular health, improves lung capacity, and enhances muscle strength. It also helps to regulate weight by burning excess calories and increases energy levels, making individuals feel more alert and productive. Exercise stimulates the release of endorphins, the body's natural mood elevators, which reduce stress and anxiety levels. Studies have shown that regular exercise can reduce the risk of chronic diseases such as heart disease, diabetes, and hypertension. In addition to the physical benefits, exercise plays a significant role in improving mental health by boosting self-esteem, reducing symptoms of depression, and enhancing cognitive function.  Activities such as hiking, cycling, and outdoor yoga are particularly beneficial. Incorporating mindfulness practices, such as deep breathing or meditation during outdoor workouts, can further amplify the mental health benefits, allowing individuals to manage stress more effectively. Learning {topic} is crucial in today's {industry}. To begin, focus on {beginner_concepts}. As you advance, delve deeper into complex ideas such as {beginner_concepts}. Attending workshops or online classes can enhance your learning process, enabling you to interact with experts and peers who share the same interests, providing you with the resources needed for long-term success in your field. Continuous self-evaluation and application of knowledge gained can significantly accelerate your mastery of {topic}. Delve deeper into complex ideas such as {beginner_concepts}."
]

passages_500 = [
    "This is a passage on exercise which you need to follow.  Attending workshops or online classes can enhance your learning process. It also helps to regulate weight by burning excess calories and increases energy levels. The importance of regular physical exercise cannot be overstated in maintaining overall health and well-being. Engaging in daily physical activities such as walking, jogging, swimming, or cycling promotes cardiovascular health, improves lung capacity, and enhances muscle strength. It also helps to regulate weight by burning excess calories and increases energy levels, making individuals feel more alert and productive. Furthermore, exercise stimulates the release of endorphins, the body's natural mood elevators, which reduce stress and anxiety levels. Studies have shown that regular exercise can reduce the risk of chronic diseases such as heart disease, diabetes, and hypertension. In addition to the physical benefits, exercise plays a significant role in improving mental health by boosting self-esteem, reducing symptoms of depression, and enhancing cognitive function. Exercising outdoors, in particular, can further improve mental well-being by allowing individuals to connect with nature, reduce feelings of isolation, and breathe fresh air. {action} is essential for maintaining {object}. Without proper {action}, you might experience {symptom}. Additionally, staying hydrated and consuming a balanced diet that supports your physical efforts will further enhance the effectiveness of your workout. Supplements like vitamins, minerals, and protein shakes can also support your body’s needs during periods of high physical exertion. Adequate rest and sleep are equally vital for recovery, allowing your muscles to heal and grow stronger over time. Regular exercise after a certain age is vital for muscles as it prevents atrophy and weakness. It ensures that as people age, they maintain functional mobility, reducing the likelihood of falls and injuries. Cardiovascular exercises, combined with strength training, are particularly effective for this. More and more, experts recommend stretching exercises like yoga and Pilates to improve flexibility and posture. These exercises reduce the likelihood of strain and injury, keeping joints flexible and improving overall physical alignment. For older adults, staying physically active becomes one of the most critical factors in maintaining independence and quality of life. Regular exercise also improves balance, coordination, and mental alertness, which all contribute to healthier aging. Exercising outdoors, in particular, can further improve mental well-being by allowing individuals to connect with nature, reduce feelings of isolation, and breathe fresh air. {action} is essential for maintaining {object}.",
"This is a passage on the importance of exercise. The importance of regular physical exercise cannot be overstated in maintaining overall health and well-being. It also helps to regulate weight by burning excess calories and increases energy levels. Engaging in daily physical activities such as walking, jogging, swimming, or cycling promotes cardiovascular health, improves lung capacity, and enhances muscle strength. It also helps to regulate weight by burning excess calories and increases energy levels, making individuals feel more alert and productive. Furthermore, exercise stimulates the release of endorphins, the body's natural mood elevators, which reduce stress and anxiety levels. Studies have shown that regular exercise can reduce the risk of chronic diseases such as heart disease, diabetes, and hypertension. In addition to the physical benefits, exercise plays a significant role in improving mental health by boosting self-esteem, reducing symptoms of depression, and enhancing cognitive function. Exercising outdoors, in particular, can further improve mental well-being by allowing individuals to connect with nature, reduce feelings of isolation, and breathe fresh air. Outdoor activities like hiking or biking provide both physical and mental stimulation, increasing your exposure to nature and natural sunlight, which boosts Vitamin D production.Group exercises, such as yoga classes or team sports, foster a sense of community and social interaction, which is critical in reducing feelings of loneliness and improving overall life satisfaction. The recommended amount of {entity} for {person} is around {amount}. This is based on the latest health guidelines, which suggest incorporating a balance of aerobic and strength-training exercises to maximize health benefits. Exercise is great, but it’s also crucial to ensure you’re practicing proper form and techniques to avoid injuries. Strengthening your core is another vital component often overlooked in many exercise routines. A strong core improves posture, reduces back pain, and makes daily activities, such as bending or lifting, easier and safer. Incorporating core-focused exercises such as planks, bridges, and sit-ups into your regular routine can significantly enhance overall fitness. Don't forget to cool down after exercise with proper stretches to maintain flexibility. Additionally, group exercises, such as yoga classes or team sports, foster a sense of community and social interaction, which is critical in reducing feelings of loneliness and improving overall life satisfaction. The recommended amount of {entity} for {person} is around {amount}. Studies have shown that regular exercise can reduce the risk of chronic diseases such as heart disease, diabetes, and hypertension.",
"The importance of regular physical exercise cannot be overstated in maintaining overall health and well-being. Engaging in daily physical activities such as walking, jogging, swimming, or cycling promotes cardiovascular health, improves lung capacity, and enhances muscle strength. It also helps to regulate weight by burning excess calories and increases energy levels, making individuals feel more alert and productive. Furthermore, exercise stimulates the release of endorphins, the body's natural mood elevators, which reduce stress and anxiety levels. Studies have shown that regular exercise can reduce the risk of chronic diseases such as heart disease, diabetes, and hypertension. In addition to the physical benefits, exercise plays a significant role in improving mental health by boosting self-esteem, reducing symptoms of depression, and enhancing cognitive function. Exercising outdoors can improve mental well-being by allowing individuals to connect with nature, reduce feelings of isolation, and breathe fresh air. {action} is essential for maintaining {object}. Without proper {action}, you might experience {symptom}. Staying hydrated and consuming a balanced diet that supports your physical efforts will further enhance the effectiveness of your workout. Supplements like vitamins, minerals, and protein shakes can also support your body’s needs during periods of high physical exertion. Adequate rest and sleep are equally vital for recovery, allowing your muscles to heal and grow stronger over time. The exercise should also help one recover from surgery. It also prevents aging, allowing individuals to maintain their vitality and mobility well into their later years. For people recovering from injuries or surgeries, physical rehabilitation through light exercise can aid in a quicker and more effective recovery. Regular movement prevents stiffness in joints and helps restore strength. Beyond physical health, exercise nurtures mental resilience. Do regular exercise when you are young. The importance of regular physical exercise cannot be overstated in maintaining overall health and well-being. Engaging in daily physical activities such as walking, jogging, swimming, or cycling promotes cardiovascular health, improves lung capacity, and enhances muscle strength. Furthermore, exercise stimulates the release of endorphins, the body's natural mood elevators, which reduce stress and anxiety levels. Exercising outdoors, in particular, can further improve mental well-being by allowing individuals to connect with nature, reduce feelings of isolation, and breathe fresh air. {action} is essential for maintaining {object}. Without proper {action}, you might experience {symptom}. Attending workshops or online classes can enhance your learning process",
"The Education and Learning {topic} is crucial in today's {industry}. As you advance, delve deeper into complex ideas such as {beginner_concepts}. Attending workshops or online classes can enhance your learning process, enabling you to interact with experts and peers who share the same interests, providing you with the resources needed for long-term success in your field. Continuous self-evaluation and application of knowledge gained can significantly accelerate your mastery of {topic}. Additionally, fitness programs often include mindfulness practices, helping individuals balance both mental and physical well-being. Many people find that adopting breathing techniques during exercise significantly enhances their performance, helping them to pace themselves more effectively. Consult the doctor before doing any hard exercises. The importance of regular physical exercise cannot be overstated in maintaining overall health and well-being. Engaging in daily physical activities such as walking, jogging, swimming, or cycling promotes cardiovascular health, improves lung capacity, and enhances muscle strength. It also helps to regulate weight by burning excess calories and increases energy levels, making individuals feel more alert and productive. Exercise stimulates the release of endorphins, the body's natural mood elevators, which reduce stress and anxiety levels. Studies have shown that regular exercise can reduce the risk of chronic diseases such as heart disease, diabetes, and hypertension. In addition to the physical benefits, exercise plays a significant role in improving mental health by boosting self-esteem, reducing symptoms of depression, and enhancing cognitive function. Activities such as hiking, cycling, and outdoor yoga are particularly beneficial. Incorporating mindfulness practices, such as deep breathing or meditation during outdoor workouts, can further amplify the mental health benefits, allowing individuals to manage stress more effectively. Learning {topic} is crucial in today's {industry}. To begin, focus on {beginner_concepts}. As you advance, delve deeper into complex ideas such as {beginner_concepts}. The Online classes can enhance your learning process, enabling you to interact with experts and peers who share the same interests, providing you with the resources needed for long-term success in your field. Continuous self-evaluation and application of knowledge gained can significantly accelerate your mastery of {topic}. Additionally, fitness programs often include mindfulness practices, helping individuals balance both mental and physical well-being. Many people find that adopting breathing techniques during exercise significantly enhances their performance, helping them to pace themselves more effectively. Delve deeper into complex ideas such as {beginner_concepts}."



    ] 

tokenizer = AutoTokenizer.from_pretrained('intfloat/multilingual-e5-base')

def generate_synthetic_query_input(num_queries):
    """Generates synthetic query input text with controlled token size."""
    queries = [
        "how much {entity} does {person} need in a day once in a while when sick?",    
        "what is the process of making {dish} in a country like North Korea?",
        "why is {concept} important for {profession}, is it really necessary to learn it?",
        "how does {action} affect {object}? Explain in brief without making judgements.",
        "can you explain {topic} to a beginner? You can use any help like AI for your help"
    ]
    
    synthetic_queries = []
    entities = ["protein", "vitamin D", "water", "calories"]
    persons = ["a female", "a male", "an athlete", "a child"]
    dishes = ["pumpkin soup", "pasta", "salad", "fried rice"]
    concepts = ["exercise", "good nutrition", "hydration", "sleep"]
    professions = ["athletes", "students", "software engineers", "teachers"]
    actions = ["drinking water", "eating", "exercise"]
    objects = ["muscles", "brain", "bones", "energy levels"]
    topics = ["nutrition", "exercise", "coding", "data science"]

    for _ in range(num_queries):
        template = random.choice(queries)
        query = template.format(
            entity=random.choice(entities),
            person=random.choice(persons),
            dish=random.choice(dishes),
            concept=random.choice(concepts),
            profession=random.choice(professions),
            action=random.choice(actions),
            object=random.choice(objects),
            topic=random.choice(topics)
        )
        query_text = f"query: {query}"
        synthetic_queries.append(query_text)

        
    return synthetic_queries

def generate_synthetic_passage_input(passages, num_passages=5):
    """Generates synthetic passage input text with controlled token size."""

    synthetic_passages = []
    entities = ["protein", "vitamin D", "water", "calories"]
    persons = ["a female", "a male", "an athlete", "a child"]
    amounts = ["46 grams per day", "600 IU", "8 cups", "2000 calories"]
    dishes = ["pumpkin soup", "pasta", "salad", "fried rice"]
    ingredients = ["pumpkin", "pasta", "olive oil", "garlic", "onions"]
    concepts = ["good nutrition", "hydration", "sleep", "exercise"]
    goals = ["high performance", "mental clarity", "optimal health"]
    reasons = ["better focus", "increased energy", "improved muscle recovery"]
    actions = ["drinking water", "eating healthy", "sleeping enough"]
    objects = ["energy levels", "muscles", "bones", "brain"]
    symptoms = ["fatigue", "muscle cramps", "headaches"]
    topics = ["coding", "nutrition", "exercise"]
    industries = ["tech industry", "fitness world", "education sector"]
    beginner_concepts = ["basics of syntax", "functions and variables", "data structures"]

    for _ in range(num_passages):
        template = random.choice(passages)
        passage = template.format(
            entity=random.choice(entities),
            person=random.choice(persons),
            amount=random.choice(amounts),
            dish=random.choice(dishes),
            ingredients=", ".join(random.sample(ingredients, 3)),
            profession=random.choice(["athletes", "teachers", "engineers"]),
            concept=random.choice(concepts),
            goal=random.choice(goals),
            reason=random.choice(reasons),
            action=random.choice(actions),
            object=random.choice(objects),
            symptom=random.choice(symptoms),
            topic=random.choice(topics),
            industry=random.choice(industries),
            beginner_concepts=random.choice(beginner_concepts)
        )
        passage_text = f"passage: {passage}"
        
        # encoding = tiktoken.get_encoding('cl100k_base')
        # print("printing tokens", len(encoding.encode(passage_text)))
        
        synthetic_passages.append(passage_text)
    
    return synthetic_passages



def main_test(input_texts):
    inputs = []
    outputs = []
    #input_texts = [" ".join(["The"] * 256)] * 256
    input = httpclient.InferInput("text", [len(input_texts),], "BYTES")
    input.set_data_from_numpy(np.array(input_texts, dtype=object), binary_data=False)
    inputs.append(input)
    
    

    outputs.append(httpclient.InferRequestedOutput("sentence_embedding", binary_data=False))

    triton_client = httpclient.InferenceServerClient(
                url="localhost:8000", verbose=False
            )
    results = triton_client.infer(
        "ensemble_model",
        inputs,
        outputs=outputs,
    )

    embeddings = results.as_numpy("sentence_embedding")

    embeddings = results.as_numpy("sentence_embedding")
    print(embeddings)

def main(input_texts):
    try:
        # Create a Triton client
        client = httpclient.InferenceServerClient(url=url)
        encoded_inputs = tokenizer(input_texts, max_length=512, padding=True, truncation=True, return_tensors='pt')

        # Convert PyTorch tensors to NumPy arrays and cast to int64
        input_ids = encoded_inputs['input_ids'].numpy().astype(np.int64)  # Model expects INT64
        attention_mask = encoded_inputs['attention_mask'].numpy().astype(np.int64)  # Model expects INT64

        # Debugging: Print shapes and data types to confirm input data
        print(f"Input_ids shape: {input_ids.shape}, dtype: {input_ids.dtype}")
        print(f"Attention_mask shape: {attention_mask.shape}, dtype: {attention_mask.dtype}")

    # Create Triton input tensors
        inputs = []
        inputs.append(httpclient.InferInput("input_ids", input_ids.shape, "INT64"))  # Use INT64 for input_ids
        inputs.append(httpclient.InferInput("attention_mask", attention_mask.shape, "INT64"))  # Use INT64 for attention_mask

        # Set the data for the input tensors
        inputs[0].set_data_from_numpy(input_ids)
        inputs[1].set_data_from_numpy(attention_mask)

    # Create Triton output tensors (for receiving results)
        outputs = []
        outputs.append(httpclient.InferRequestedOutput("sentence_embedding"))
        outputs.append(httpclient.InferRequestedOutput("token_embeddings"))

    # Make the inference request
        response = client.infer(model_name=model_name, inputs=inputs, outputs=outputs)
        print("got response")
        # Retrieve the output data from the response
        sentence_embedding = response.as_numpy("sentence_embedding")
        token_embeddings = response.as_numpy("token_embeddings")

        #print("Sentence embedding", sentence_embedding)

        # Print the result
        print(f"Sentence Embedding Shape: {sentence_embedding.shape}")
        print(f"Token Embeddings Shape: {token_embeddings.shape}")    

    except Exception as e:
        print(f"Error during inference: {e}")
        return None


def run_hug_e5(batch_size, input_type, input_tokens):
    if input_type == 'passage':
        token_input = passages_300 if input_tokens == 300 else passages_500
        queries = generate_synthetic_passage_input(token_input, batch_size)
    else:
        queries = generate_synthetic_query_input(batch_size)

    print(len(queries))
    
    start_time = time.time()  # Record the start time
    try:
        main_test(queries)  # Run the main function of hug-e5
    except Exception as e:
        print(f"Error encountered during execution: {e}")
    
    elapsed_time = time.time() - start_time  # Calculate elapsed time
    print("Execution finished")
    print(elapsed_time)
    
    return elapsed_time



 # Define headers similar to your provided image
headers = ["Metric", "Input Type", "Input Tokens", "Batch Size", "Concurrency", "Avg (ms)", "Min (ms)", 
            "Max (ms)", "P99 (ms)", "P95 (ms)", "P90 (ms)", "P75 (ms)", "P50 (ms)", "P25 (ms)", 
            "Throughput (inputs/s)"]

table_data = []



def run_benchmark(number_of_runs, max_workers, batch_size, input_type, input_tokens):
    latencies = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_hug_e5, batch_size, input_type, input_tokens)
                   for _ in range(number_of_runs * max_workers)]
        for future in as_completed(futures):
            latencies.append(future.result())

    print("thread pool done!")
    avg_latency = np.mean(latencies)
    min_latency = np.min(latencies)
    max_latency = np.max(latencies)
    # Calculate required metrics
    p25_latency, p50_latency, p75_latency, p90_latency, p95_latency, p99_latency = np.percentile(
        latencies, (25, 50, 75, 90, 95, 99))

    throughput = 1 / avg_latency if avg_latency > 0 else 0  # Throughput is the inverse of average latency

    table_data.append(["Request Latency (ms)", input_type, input_tokens, batch_size, max_workers,
        f"{avg_latency * 1000:.2f}", f"{min_latency * 1000:.2f}", f"{max_latency * 1000:.2f}",
        f"{p99_latency * 1000:.2f}", f"{p95_latency * 1000:.2f}", f"{p90_latency * 1000:.2f}",
        f"{p75_latency * 1000:.2f}", f"{p50_latency * 1000:.2f}", f"{p25_latency * 1000:.2f}",
        f"{throughput:.2f}"])



def start_benchmarking():
    data = [
        (1, 64, 'passage', 300),
        (3, 64, 'passage', 300),
        (5, 64, 'passage', 300),
        (1, 64, 'passage', 500),
        (3, 64, 'passage', 500),
        (5, 64, 'passage', 500),
        (1, 1, 'query', 20),
        (3, 1, 'query', 20),
        (5, 1, 'query', 20),
        (7, 1, 'query', 20),
        (11, 1, 'query', 20),
        (13, 1, 'query', 20),
        (15, 1, 'query', 20)
    ]

    for max_workers, batch_size, input_type, input_tokens in data:
        run_benchmark(200, max_workers, batch_size, input_type, input_tokens)    
        print(f"benchmarking completed for {input_type} with {input_tokens} input tokens and {max_workers} threads and {batch_size} batch size")


    html_table = tabulate(table_data, headers=headers, tablefmt="html")
    print(html_table)


if __name__ == "__main__":
    start_benchmarking()
