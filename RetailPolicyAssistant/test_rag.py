from app.rag.pipeline import answer_policy_question

question = "Can employees accept expensive gifts from vendors?"
result = answer_policy_question(question)
print("\nANSWER\n")
print(result["answer"])
print("\nSOURCES\n")
for source in result["sources"]:
    print(source)
