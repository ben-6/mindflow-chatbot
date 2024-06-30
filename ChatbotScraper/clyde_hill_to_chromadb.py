import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
import uuid
import os
from pypdf import PdfReader
from tqdm import tqdm

extracted_path = os.environ.get("CHATBOT_PATH") + '/Data/clyde_hill_extracted'
chroma_table_path = os.environ.get("CHATBOT_PATH") + '/Data/clyde_hill_db'

embedding = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ.get('OPENAI_API_KEY'),
        model_name="text-embedding-ada-002"
    )
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
client = chromadb.Client(
    Settings(chroma_db_impl="duckdb+parquet", persist_directory=chroma_table_path))

# Create Chroma Database
collection = client.get_or_create_collection(
    name="clyde_hill_db", embedding_function=embedding)


# Iterate through all text files
print("txts")
for filename in tqdm(os.listdir(extracted_path)):
    file_path = os.path.join(extracted_path, filename)
    
    if filename.endswith('.txt'):
        with open(file_path, 'r') as file:
            # Website metadata is stored at top of extracted text files.

            source = file.readline().strip()
            title = file.readline().strip()
            date = file.readline().strip()
            
            content = file.read().strip()
            
            print("File:", filename)
            
            chunks = text_splitter.split_text(content)
            if len(chunks):
                # Chunks that are too big are split into multiple database entries.
                if len(chunks) > 950:
                    while len(chunks) > 950:
                        collection.add(
                            documents=chunks[:950], 
                            metadatas=[{"url": source, "title": title, "date": date}]*len(chunks[:950]), 
                            ids=[str(uuid.uuid4()) for _ in range(len(chunks[:950]))])
                        chunks = chunks[950:]
                else:
                    collection.add(
                            documents=chunks[:], 
                            metadatas=[{"url": source, "title": title, "date": date}]*len(chunks[:]), 
                            ids=[str(uuid.uuid4()) for _ in range(len(chunks[:]))])
                
                    
def extract_pdf_text(pdf_filename):
    with open(pdf_filename, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file, strict=False)
        pdf_text = ''
        pdf_title = "City of Clyde Hill"
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()
        if pdf_reader.metadata:
            pdf_title = pdf_reader.metadata.title
            if pdf_title == None:
                # Placeholder title if no title found
                pdf_title = "City of Clyde Hill"
        
        return pdf_text, pdf_title

# Iterate through all pdf files
print("pdfs")
for filename in tqdm(os.listdir(extracted_path + "/pdfs")):
    file_path = os.path.join(extracted_path, filename) 

    if filename.endswith('.pdf'):
        #print("before filename", filename)
        pdf_text, pdf_title = extract_pdf_text(extracted_path + "/pdfs/" + filename)
          
        chunks = text_splitter.split_text(pdf_text)
        print(filename, pdf_title, len(chunks))  
        
        if len(chunks):
            try:
                collection.add(
                    documents=chunks[:], 
                    metadatas=[{"url": "", "title": pdf_title, "date": ""}]*len(chunks), 
                    ids=[str(uuid.uuid4()) for _ in range(len(chunks))])
            except:
                print("Broken")

client.persist()