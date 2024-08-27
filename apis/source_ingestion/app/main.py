from fastapi import FastAPI, HTTPException, Depends, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Query
from fastapi.security import OAuth2PasswordBearer
import logging
from pydantic import BaseModel, HttpUrl
from typing import Optional
import uuid
from mangum import Mangum
from app.services.cognito_service import get_current_user
from app.services.combine_cleanup_service import get_combination_cleanup_service
from app.services.content_processor_service import get_content_processor_service
from app.services.webscraper_service import get_web_scraper_service
from app.services.knowledge_source_service import get_knowledge_source_service, KnowledgeSourceCreate, KnowledgeSourceUpdate
from app.services.community_service import requires_owner, requires_member
from app.services.knowledge_source_service import KnowledgeSourceService


# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="https://your_cognito_domain/oauth2/token")

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlProcessRequest(BaseModel):
    url: HttpUrl

@app.post("/community/{community}/source-ingestion/url/")
async def process_url(
    request: UrlProcessRequest,
    community: str = Path(..., description="The community ID"),
    current_user: dict = Depends(get_current_user)
):
    logger.info(f"Processing URL for community {community}: {request.url}")
    
    # Instantiate services
    web_scraper_service = get_web_scraper_service()
    content_processor_service = get_content_processor_service()
    combination_cleanup_service = get_combination_cleanup_service()
    knowledge_source_service = get_knowledge_source_service()

    # Step 1: Create a knowledge source entry
    source_id = uuid.uuid4()
    knowledge_source = KnowledgeSourceCreate(
        source_id=source_id,
        community_id=community,
        url=request.url,
        source_status="Pending"
    )
    knowledge_source_service.create_knowledge_source(knowledge_source)

    try:
        # Step 2: Scrape the content
        scraped_content = web_scraper_service.scrape_content(request.url)
        if not scraped_content:
            raise HTTPException(status_code=500, detail="Failed to scrape content from the URL")
        
        # Step 3: Process the content with GPT-4-O
        content_processor_service.openai_controller.set_model("gpt-4o", 4096)
        system_message = (
            "You are a highly skilled educational assistant tasked with extracting, synthesizing, and organizing key information from complex content to serve as an educational tool for generating quiz questions, study materials, and comprehensive content summaries. Your goal is to deliver precise, structured, and comprehensive outputs that ensure thorough coverage of the content, including detailed metadata and core insights."
            "1. Identify the Author(s): Determine who created or contributed to the content. If multiple authors are mentioned, list them all. If no explicit author is found but the content is from an official source (e.g., company documentation), infer the organization or team responsible (e.g., 'AWS Documentation Team'). If no author can be identified, return 'unknown'."
            "2. Determine the Publication/Site: Identify the full name of the website or publication where the content is published. Use the complete publication name, not acronyms. If available, extract this information from the URL, header, or footer of the page. If the site or publication name is not explicitly stated, use the name of the organization or entity associated with the content. If the publication or site cannot be accurately determined, return 'unknown'."
            "3. Extract the Publish Date: Look for the publication date, usually near the title or byline. If the exact date is not clear, attempt to extract the last updated date from the documentation page. If no date is available, return 'unknown'."
            "4. Ascertain the Main Topic: Identify the primary focus or subject matter of the content. Summarize it in a single, clear sentence. If the main topic is unclear, return 'unknown'."
            "5. Classify the Parent Topic: Determine the broader category under which the main topic falls (e.g., 'Technology,' 'Health'). If no parent topic can be identified, return 'unknown'."
            "6. Identify the Field: Pinpoint the academic or professional field related to the content, such as 'Computer Science,' 'History,' or 'Medicine.' If the field is not clear, return 'unknown'."
            "7. Extract Keywords and People: Pull out key terms that define core concepts or topics discussed, aiming for between 10 and 30 keywords, depending on subject length. For each keyword: "
            "- Provide a Definition: Clearly define the term in the context of the article. Ensure the definition is concise yet informative."
            "- Explain Its Relation to the Topic: Elaborate on how the keyword connects to the main point or focus of the article, using specific mentions from the article to reinforce the explanation."
            "8. Summarize Major Insights or Novel Concepts: Identify and summarize key ideas, breakthroughs, or perspectives in the content. Format these insights as {'insight': 'summary of the idea', 'concept': 'related concept'}. If none are found, return an empty array '[]'."
            "9. Gather Supporting Details: Provide additional context, examples, or explanations that enrich the understanding of the major insights. Ensure this section is distinct from 'major insights' to avoid redundancy. If no supporting details are available, return an empty array '[]'."
            "10. Extract Relevant Quotations: Look for impactful or informative statements within the content to pull out as quotes. Ensure quotes are concise and directly relevant. If no relevant quotations are found, return an empty array '[]'."
            "11. Identify External Links: If the content references or links to other relevant sources, include those links. These should be useful for further reading or supporting the information presented. If no external links are found, return an empty array '[]'."
            "12. Content Chunk Summary: Summarize each chunk of content. Format the output as a clean, well-organized JSON object with all the exact keys and values mentioned. Ensure your response is concise yet thorough, delivering maximum educational value."
            "Use these examples as a guide to ensure your output aligns with the expected format. Remember to follow the steps methodically for the most accurate and valuable response."
            "Example 1: {"
            " 'author': 'John Doe', "
            " 'site': 'Example.com', "
            " 'publish_date': '2024-08-19', "
            " 'main_topic': 'The Impact of Artificial Intelligence on Healthcare', "
            " 'parent_topic': 'Technology and Medicine', "
            " 'field': 'Health Technology', "
            " 'keywords': ["
            "   {"
            "     'keyword': 'Artificial Intelligence', "
            "     'definition': 'A branch of computer science focused on creating systems capable of performing tasks that require human intelligence.', "
            "     'relation_to_topic': 'The article discusses how AI is transforming healthcare by improving diagnostic accuracy and reducing human error.'"
            "   }, "
            "   {"
            "     'keyword': 'Machine Learning', "
            "     'definition': 'A subset of AI involving the development of algorithms that allow computers to learn from and make predictions based on data.', "
            "     'relation_to_topic': 'The article highlights the role of machine learning in analyzing vast amounts of medical data to support clinical decisions.'"
            "   }"
            " ], "
            " 'major_insights_or_novel_concepts': ["
            "   {"
            "     'insight': 'AI-driven diagnostics reduce human error by applying machine learning to medical imaging.', "
            "     'concept': 'AI Diagnostics'"
            "   }"
            " ], "
            " 'supporting_details': ['Studies show a 20 percent reduction in diagnostic errors using AI.', 'Hospitals worldwide are beginning to implement AI tools, such as the Mayo Clinic’s adoption of AI for radiology.'], "
            " 'relevant_quotations': ['AI is revolutionizing healthcare, reducing errors and saving lives, says Dr. Smith, a leading expert in AI healthcare applications.'], "
            " 'external_links': ['https://example.com/ai-healthcare']"
            "} "
            
            "Example 2: {"
            " 'author': 'Jane Smith', "
            " 'site': 'ScienceDaily.com', "
            " 'publish_date': '2023-05-10', "
            " 'main_topic': 'The Role of Quantum Computing in Cryptography', "
            " 'parent_topic': 'Computer Science', "
            " 'field': 'Quantum Computing', "
            " 'keywords': ["
            "   {"
            "     'keyword': 'Quantum Computing', "
            "     'definition': 'A type of computing that uses quantum bits, or qubits, to perform calculations at speeds unattainable by classical computers.', "
            "     'relation_to_topic': 'The article explores how quantum computing challenges traditional cryptography by making current encryption methods vulnerable.'"
            "   }, "
            "   {"
            "     'keyword': 'Cryptography', "
            "     'definition': 'The practice of secure communication in the presence of third parties, often through encryption.', "
            "     'relation_to_topic': 'The article examines how advancements in quantum computing are prompting a reevaluation of cryptographic techniques.'"
            "   }"
            " ], "
            " 'major_insights_or_novel_concepts': ["
            "   {"
            "     'insight': 'Quantum computers exploit quantum mechanics to perform calculations that are infeasible for classical computers, challenging existing encryption methods.', "
            "     'concept': 'Quantum Cryptography'"
            "   }"
            " ], "
            " 'supporting_details': ['Quantum computers leverage superposition and entanglement to achieve unprecedented computational speeds.', 'Current encryption methods, like RSA, could become obsolete without quantum-resistant algorithms.'], "
            " 'relevant_quotations': ['Quantum computing poses a significant challenge to traditional encryption, necessitating a new era of cryptography, says Dr. Allen, a pioneer in the field.'], "
            " 'external_links': ['https://sciencedaily.com/quantum-cryptography']"
            "} "
            "Finally, minify your response, use double quotes for property names, and do not include any line breaks or newline characters in the JSON. The JSON FORMAT MUST BE PERFECT!!!")
        
        processed_chunks = content_processor_service.process_content(scraped_content, system_message)
        if not processed_chunks:
            raise HTTPException(status_code=500, detail="Failed to process content")

        # Step 4: Store the chunks
        knowledge_source_service.store_chunks(community, str(source_id), processed_chunks)

        # Step 5: Combine and clean up the processed content with GPT-4-O-mini
        combination_cleanup_service.openai_controller.set_model("gpt-4o-mini", 16000)
        combined_response = combination_cleanup_service.combine_responses(processed_chunks)
        final_response = combination_cleanup_service.clean_up_response(combined_response)

        # Step 6: Store the combined output
        knowledge_source_service.store_combined_output(community, str(source_id), final_response)

        # Step 7: Update the knowledge source status
        knowledge_source_update = KnowledgeSourceUpdate(status="Completed")
        knowledge_source_service.update_knowledge_source(community, str(source_id), knowledge_source_update)

    except Exception as e:
        # Update the knowledge source status in case of failure
        knowledge_source_update = KnowledgeSourceUpdate(source_status="Failed")
        knowledge_source_service.update_knowledge_source(community, str(source_id), knowledge_source_update)
        raise e

    return {
        "community": community,
        "url": request.url,
        "summary": final_response
    }

@requires_member('community')
@app.get("/community/{community}/knowledge-sources/")
def list_knowledge_sources(
    community: str,
    limit: int = Query(20, description="Number of items to return"),
    last_evaluated_key: Optional[str] = Query(None, description="Token for pagination"),
    knowledge_source_service: KnowledgeSourceService = Depends(get_knowledge_source_service),
    current_user: dict = Depends(get_current_user)
):
    items, last_key = knowledge_source_service.list_knowledge_sources(community, limit, last_evaluated_key)
    return {"items": items, "next_token": last_key}

@requires_owner('community')
@app.delete("/community/{community}/knowledge-source/{source_id}")
def delete_knowledge_source(
    community: str,
    source_id: uuid.UUID,
    knowledge_source_service: KnowledgeSourceService = Depends(get_knowledge_source_service)
):
    knowledge_source_service.delete_knowledge_source(community, str(source_id))
    return {"message": "Knowledge source deleted successfully"}


handler = Mangum(app)
