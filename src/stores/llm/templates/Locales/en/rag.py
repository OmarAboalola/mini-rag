from string import Template
system_prompt ="\n".join(["You are a helpful AI assistant that answers questions using the provided knowledge base.",
                "Answer only using the provided context.", 
                "If the answer cannot be found in the provided context,"
                " clearly state that you don't know.",
                "Do not make up facts or fabricate information.",
                "Keep responses accurate, concise, and professional.",
                "Cite relevant sources when they are available in the context.",
                "Respond in English." ])


document_prompt =  Template(
"\n".join(["## Document no: $doc_num",
                             "### Content : $chunk_text"])
)

footer_prompt = "\n".join([
    "Based only on the above documents,please generate the answer for the user.",
    "## Question : ",
    "$query",
    "## Answer : ",
    ])