from openai import OpenAI

# TODO Load this prompts from assets folder
system_prompt = """
Your task is to generate flashcards based on the input text to promote student learning. Create the cards in the format "front;back". Proceed as follows:
1. Identify all key concepts and formulate in-depth comprehension questions (front side) that require detailed answers (back side). Add information
and context as appropriate. Mark these cards with the prefix [Concept].
2. Create critical thinking questions that build on but go beyond the concepts in the text. These should make up one-third of all questions. Label these with the prefix [Critical Thinking].
3. Finally, create an flashcard for each technical term in the text with the definition on the back. Label these cards with the prefix [Term].
Make sure that the language of the flashcards always corresponds to the original language of the text.
"""

user_prompt = """
Recognition characteristics of cancer
Cancers are characterized by uncontrolled cell growth and division. There are certain hallmarks of cancer that are very common in many types of
cancer. Cancer cells must not only continue to divide, but also find ways to prevent death. When cells accumulate large amounts of DNA damage, they
usually undergo programmed cell death, known as apoptosis. Another barrier is the immune system, which is constantly on the hunt for cancer and kills
cells with certain DNA damage. Some of the most common cancer mutations (such as p53) therefore prevent apoptosis or help evade the immune system.
Genome instability is another hallmark of cancer. A combination of just a handful of specific mutations is sufficient to initiate cancer. However,
enough mutations must first accumulate to hit these highly carcinogenic oncogenes and tumor suppressors. An increase in the mutation rate, therefore,
correlates with the number of mutations that accumulate. Such an increase in mutation rate is referred to as genome instability.
"""

assistent_answer = """
[Concept] What are the characteristic features of all types of cancer?; The characteristic feature of all types of cancer is uncontrolled cell division, avoidance of programmed cell death (apoptosis), and evasion from the immune system.
[Concept] Why is defective apoptosis a common cancer trigger?; DNA damage normally triggers programmed cell death at cell cycle checkpoints. This prevents the defective cell from dividing, generating exponentially defective cells, and increasing the likelihood of malignant mutations and cancer.
[Concept] Why do cancer cells need to evade the immune system?; The immune system targets cells with specific types of DNA damage, so cancer cells must avoid detection in order to survive and proliferate.
[Concept] What is the significance of genome instability on cancer?; Genome instability increases the mutation rate, allowing more mutations to accumulate in cells. This increases the likelihood of mutations in oncogenes and tumor suppressors that can initiate or drive cancer.
[Critical Thinking] When considering the various sources of mutations in cancer, which source is potentially most avoidable and why?; Errors in DNA replication are a natural process and hard to prevent. However, exposure to carcinogens like cigarette smoke or harmful radiation can be limited or avoided, making these sources of mutations more avoidable.
[Critical Thinking] Could the immune system be manipulated to work more efficiently against cancer? If yes, how?; Yes, through immunotherapies the immune system could be strengthened or "reprogrammed" to more efficiently recognize and destroy cancer cells. Techniques such as CAR-T cell therapy or checkpoint inhibitors could play a role here.
[Term] Apoptosis; Apoptosis is the programmed cell death through which the body eliminates damaged or abnormal cells.
[Term] Oncogene; An oncogene is a gene whose mutation or excessive activation can promote cell growth and division.
[Term] Tumor suppressor; A tumor suppressor is a gene that regulates cell division and has the potential to suppress tumor growth.
[Term] Genome instability; Genome instability is the condition of increased susceptibility to changes in the DNA sequence of an organism.
"""

class Flashcard:
    def __init__(self, front="", back=""):
        self.front = front
        self.back = back

def generate_flashcards(request: str) -> list[Flashcard]:
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user","content": user_prompt},
            {"role": "assistant","content": assistent_answer},
            {"role": "user","content": "Create flashcards based on the following text:"},
            {"role": "user","content": request},
        ]
    )

    answer = completion.choices[0].message.content

    # TODO Convert answer to list of flashcards objects and return

    return answer