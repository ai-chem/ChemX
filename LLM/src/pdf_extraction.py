import sys
import argparse, os, os.path
import pandas as pd
from tqdm import tqdm
import json

from openai import OpenAI
from openai.types.beta.threads.message_create_params import Attachment, AttachmentToolFileSearch

from constants import DATASETS, MAGNETIC_ARTICLES, SELTOX_ARTICLES

def get_parameters() -> argparse.Namespace:
    """Parses and returns command-line arguments for dataset selection and OpenAI API key."""
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--openai_api_key', type=str, required=True)
    parser.add_argument('--dataset', type=str, choices=DATASETS, required=True)
    return parser.parse_args()

def get_query(dataset: str) -> tuple[str, str]:
    """Retrieves prompt components for a specified dataset."""
    df_promt = pd.read_csv('data/prompts.csv')
    description = df_promt['description'][df_promt['dataset'] == dataset].item()
    instructions = df_promt['instructions'][df_promt['dataset'] == dataset].item()
    prompt = df_promt['prompt'][df_promt['dataset'] == dataset].item()
    return description, instructions, prompt

def get_query_by_condition(dataset: str, condition: str) -> tuple[str, str]:
    """Retrieves prompt components for a specified dataset by condition (for 'complexes' dataset)."""
    df_promt = pd.read_csv('data/prompts.csv')
    description = df_promt['description'][(df_promt['dataset'] == dataset) & (df_promt['condition'] == condition)].item()
    instructions = df_promt['instructions'][(df_promt['dataset'] == dataset) & (df_promt['condition'] == condition)].item()
    prompt = df_promt['prompt'][(df_promt['dataset'] == dataset) & (df_promt['condition'] == condition)].item()
    return description, instructions, prompt

def main() -> None:
    """
    Main entry point for information extraction from PDF documents using OpenAI's GPT-4o model.

    This function:
        - Parses command-line arguments to retrieve the dataset name and OpenAI API key.
        - Loads a list of open-access PDF files associated with the dataset.
        - Checks the presence of these PDFs in the appropriate folders.
        - For each PDF, constructs dataset-specific prompts.
        - Uses OpenAI's Assistants API to upload the PDF file, send a prompt, generate a structured response using a predefined JSON schema.
        - Collects the output into a DataFrame and saves it as a CSV file.
    """
    args = vars(get_parameters())
    api_key = args['openai_api_key']
    dataset = args['dataset']
    
    client = OpenAI(api_key=api_key)

    # pdfs
    path_to_pdfs = f'data/pdfs/pdf_{dataset}/'
    path_to_merged_pdfs = f'data/pdfs/pdf_{dataset}_merged/'
    pdf_files = os.listdir(path_to_pdfs)
    if os.path.isdir(path_to_merged_pdfs) == True:
        pdf_files.extend(os.listdir(path_to_merged_pdfs))
    # promt
    if dataset != 'complexes':
        description, instructions, prompt = get_query(dataset)
    # dataset
    df_dataset = pd.read_csv(f'data/datasets/{dataset}.csv')

    # open access files from dataset
    if dataset in ['complexes', 'nanozymes', 'oxazolidinone', 'benzimidazole']: # pdf column
        access_files = set(df_dataset['pdf'].apply(lambda x: x + '.pdf')[df_dataset['access'] == 1])
    elif dataset in ['cytotoxicity', 'synergy']: # pdf column with .pdf
        access_files = set(df_dataset['pdf'][df_dataset['access'] == 1])
    elif dataset in ['cocrystals']: # select name of pdf without suppl
        access_files = set(df_dataset['pdf'].apply(lambda x: x.split(',')[0] + '.pdf')[df_dataset['access'] == 1])
    elif dataset == 'magnetic': # too many open access pdfs, working with half of them
        access_files = MAGNETIC_ARTICLES
        print(access_files, len(access_files))
    elif dataset == 'seltox': # too many open access pdfs, working with half of them
        access_files = SELTOX_ARTICLES
        print(access_files, len(access_files))
    else:
        sys.exit('No code for this!')

    # check presence of pdfs
    lower_access_files = set([x.lower() for x in access_files])
    intersec = lower_access_files.intersection(set([x.lower() for x in pdf_files]))
    if len(access_files) == len(intersec):
        print('All pdfs in the folder!')
    else:
        print(f'Check pdfs! {list(lower_access_files - intersec)} are missing')

    # start extraction
    print(f'Working with {len(access_files)} pdfs...')

    with open(f'data/json/{dataset}.json', 'r') as file:
        structure_json = json.load(file)

    df = pd.DataFrame(columns=['pdf', 'description', 'instructions', 'prompt', 'output'])

    for pdf in tqdm(access_files):
        
        if dataset == 'complexes':
            description, instructions, prompt = get_query_by_condition(dataset, df_dataset['metal'][df_dataset['pdf'] == pdf[:-4]].iloc[0])
        
        path = path_to_merged_pdfs + pdf
        if os.path.isfile(path) == False:
            path = path_to_pdfs + pdf
        print(f'Extraction from {path} ...')
        
        file = client.files.create(
            file=open(path, 'rb'),
            purpose='assistants')
        
        thread = client.beta.threads.create()
        
        client.beta.threads.messages.create(
            thread_id = thread.id,
            role='user',
            content=prompt,
            attachments=[Attachment(file_id=file.id, tools=[AttachmentToolFileSearch(type='file_search')])])
        
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=client.beta.assistants.create(
                model='gpt-4o',
                description=description,
                instructions=instructions,
                tools=[{"type": "file_search"}],
                name='My Assistant Name',
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": dataset,
                        "schema": structure_json,
                        "strict": True,
                        },
                    },
                ).id,
            timeout=300)
        
        if run.status != "completed":
            raise Exception('Run failed:', run.status)
        
        messages_cursor = client.beta.threads.messages.list(thread_id=thread.id)
        messages = [message for message in messages_cursor]
        message = messages[0]
        assert message.content[0].type == "text"
        result = message.content[0].text.value
        client.files.delete(file.id)
        
        df.loc[len(df)] = [pdf, description, instructions, prompt, result]
        df.to_csv(f'result/from_pdf/{dataset}_result.csv', index=False)

if __name__ == "__main__":
    main()
    


