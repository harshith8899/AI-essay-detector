"""One-off script: writes the manually-authored DEVELOPMENT dataset to disk.

Every essay below was written by hand (by the assistant, at the user's
explicit request, as an offline authoring task) as a stand-in for a real
corpus. None of these are real applicants' essays, and the "ai_" essays
were NOT produced by calling an external LLM API — no API is configured in
this project. They are hand-written imitations of typical AI-generated
admissions-essay prose (heavy on cliches, transition-word openers, and
generic uplift), used only so the Phase 3/4 pipeline has something to run
on. See data/README.md for the full, honest account of what this dataset
is and is not.

Run once from backend/:
    python -m scripts.seed_dev_dataset
"""

import json
from pathlib import Path

from app.spacy_pipeline import nlp
from scripts.generate_polished import sentence_diff

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
HUMAN_DIR = DATA_DIR / "human_essays"
AI_DIR = DATA_DIR / "ai_essays"
POLISHED_DIR = DATA_DIR / "polished_essays"

GENERATED_AT = "2026-08-15T00:00:00Z"

# ---------------------------------------------------------------------------
# Human essays (development placeholders, manually authored)
# ---------------------------------------------------------------------------

HUMAN_ESSAYS = {
    "human_001": (
        "topic",
        "learning carpentry from a grandparent",
        "I didn't expect to fall in love with the smell of sawdust, but that's "
        "exactly what happened the summer I started helping my grandfather in "
        "his garage. He'd hand me a piece of scrap wood and just say 'see what's "
        "in there,' which honestly annoyed me at first because I wanted "
        "instructions, not riddles. My first birdhouse leaned so badly it looked "
        "drunk. He laughed, didn't fix it for me, and told me to try again. By "
        "August I was the one telling him to slow down and let me finish a cut. "
        "I still have that lopsided birdhouse on a shelf in my room."
    ),
    "human_002": (
        "topic",
        "debate team failure and growth",
        "My first debate round lasted four minutes before I forgot my entire "
        "argument and just stood there. The judge actually put her pen down. I "
        "wanted to quit that night, but my partner texted me a single word: "
        "'again.' So we drilled rebuttals in her basement every Tuesday for a "
        "month. I lost my next six rounds too, honestly, but by the regional "
        "tournament I could feel the argument forming while the other team was "
        "still talking. We didn't win state. We got to the semifinal, and I "
        "didn't freeze once, which felt like winning anyway."
    ),
    "human_003": (
        "topic",
        "grandmother's recipe and family kitchen",
        "My grandmother measures flour with her hand, not a cup, and for years I "
        "couldn't replicate her bread no matter how hard I tried. She'd watch me "
        "knead and just shake her head. One Sunday she finally put her hands over "
        "mine instead of explaining, and something clicked that no recipe card "
        "ever could. Now when relatives visit, I'm the one making the dough while "
        "she critiques the crust from her chair. It's not really about the bread. "
        "It's the only time all of us are quiet together in the same room."
    ),
    "human_004": (
        "topic",
        "volunteering at an animal shelter",
        "The first dog I worked with at the shelter bit through my glove, and I "
        "almost didn't come back the next Saturday. But nobody there acted like "
        "that was a big deal, so I showed up anyway. Six months later that same "
        "dog, Biscuit, fell asleep with his head on my shoe during a slow shift. "
        "I've cleaned more kennels than I can count and cried in the parking lot "
        "twice when dogs got adopted, which doesn't make sense but happens every "
        "time. I'm not sure I'm helping the shelter as much as it's helping me."
    ),
    "human_005": (
        "topic",
        "stage fright and learning guitar",
        "I threw up before my first guitar recital, which nobody tells you is a "
        "real possibility. My hands shook so badly during the intro that I "
        "started a full step off from everyone else. I wanted to walk offstage. "
        "Instead I just stopped, looked at my teacher in the front row, and "
        "restarted. Nobody clapped, but nobody laughed either. Three recitals "
        "later I still get nervous, but it's the kind of nervous that feels more "
        "like readiness than dread, and that difference took me two years to "
        "actually notice."
    ),
    "human_006": (
        "topic",
        "working at the family restaurant",
        "My family's restaurant has one dishwasher, and for most of high school "
        "that dishwasher was me. I used to resent every Friday night shift while "
        "my friends were out. But somewhere between the third and fourth summer "
        "I started noticing regulars by their orders before they sat down, and my "
        "dad started asking my opinion on the new menu items. I still don't love "
        "washing dishes. I do love that Mrs. Alvarez always asks for me by name "
        "now, and that my dad trusts me to close on my own."
    ),
    "human_007": (
        "topic",
        "robotics club competition failure",
        "Our robot's arm snapped off thirty seconds into the qualifying round, "
        "in front of the one judge who'd been the toughest on us all season. My "
        "teammate wanted to cry, and honestly so did I. We spent that night in a "
        "hotel bathroom with a hot glue gun and a roll of duct tape trying "
        "anything. It held for exactly one more match, which was enough to not "
        "finish last. We didn't advance. But I learned more about torque, and "
        "about staying calm when something breaks in front of everyone, than any "
        "match we actually won."
    ),
    "human_008": (
        "topic",
        "immigrating and learning a new language",
        "I moved here when I was eleven and understood maybe one word out of ten "
        "in my first English class. I used to write down phrases phonetically in "
        "the back of my notebook just to survive lunch conversations. My teacher, "
        "Ms. Reyes, let me answer questions in writing before I could say them out "
        "loud, which sounds small but wasn't. By eighth grade I was translating "
        "for my mother at parent-teacher conferences. I still think in two "
        "languages depending on the subject, and I've stopped apologizing for the "
        "accent that shows up when I'm tired."
    ),
    "human_009": (
        "topic",
        "caring for a younger sibling",
        "When my mom got sick sophomore year, I started doing my little sister's "
        "hair before school because nobody else was going to. I didn't know how "
        "at first, and there were a lot of crooked braids and a lot of tears, "
        "mostly mine. She's seven now and tells anyone who'll listen that I do "
        "the best braids in the family, which isn't true but I never correct her. "
        "My mom is better now, but I still do the hair most mornings because we "
        "both, quietly, like the routine we built when things were hard."
    ),
    "human_010": (
        "topic",
        "cross country injury and comeback",
        "A stress fracture ended my sophomore cross country season three weeks "
        "before regionals, and I spent that fall watching from the sideline in a "
        "walking boot. It was miserable in a way that's hard to explain to people "
        "who don't run. My coach had me keep a training log anyway, just "
        "writing down how I felt each day, even doing nothing. When I finally "
        "raced again that spring I was slower than I'd ever been. I finished "
        "dead last in my first meet back and felt more proud crossing that line "
        "than I had at any race before the injury."
    ),
    "human_011": (
        "topic",
        "building a small app for a grandparent",
        "My grandmother kept missing her medication times, so I built her a "
        "clunky little app over one winter break that just buzzed her phone at "
        "the right hours. My first version crashed constantly and sent "
        "notifications at 3 a.m. twice before I fixed the bug. She still calls it "
        "'the pill thing' and shows it off to her neighbors like it's magic, even "
        "though it's maybe two hundred lines of code held together with "
        "patience. It's not sophisticated. But it's the first thing I ever built "
        "that another person actually depends on."
    ),
    "human_012": (
        "topic",
        "starting a community garden",
        "The lot next to our apartment building was just weeds and broken glass "
        "until three of us neighbors got tired of looking at it. We had no idea "
        "what we were doing and killed most of our first tomato plants by "
        "overwatering them out of pure anxiety. Mrs. Okafor from the third floor "
        "turned out to know everything about soil, and she basically became our "
        "unofficial teacher. Two summers later the garden feeds six families and "
        "somehow also became the place where people actually talk to their "
        "neighbors, which the lot never did as weeds."
    ),
    "human_013": (
        "topic",
        "learning to skateboard after breaking an arm",
        "I broke my arm the second week I tried skateboarding, which felt like "
        "a pretty clear sign to stop. My mom certainly thought so. But six weeks "
        "in a cast just made me watch more videos and get more stubborn about "
        "it, and the day the cast came off I was back at the same curb. I still "
        "can't land a kickflip consistently, maybe one in twenty tries, but I "
        "can ollie up a curb now without thinking about it, which used to feel "
        "impossible. My mom has stopped asking me to stop and started asking me "
        "to wear the wrist guards instead."
    ),
    "human_014": (
        "topic",
        "museum internship and discovering art history",
        "I took the museum internship because it filled a gap in my summer "
        "schedule, not because I cared about art. I spent the first two weeks "
        "just dusting frames and reading wall labels out of boredom. Then a "
        "visiting curator explained why one particular portrait's brushstrokes "
        "mattered, and something shifted for me that I still can't fully explain. "
        "I started staying late to read the catalog files nobody asked me to "
        "read. I came in expecting a resume line and left with a section of the "
        "museum I now know better than most of the staff."
    ),
    "human_015": (
        "topic",
        "working part-time at a bookstore",
        "I took the bookstore job because it was close to home, not because I "
        "particularly loved retail. But you learn a lot about people from what "
        "they buy at 9 p.m. on a Tuesday. Regulars started asking me for "
        "recommendations, and I started keeping a mental list of who liked what, "
        "which the owner eventually just let me build into an actual shelf of "
        "staff picks. My picks are wrong sometimes and people tell me so, "
        "bluntly, which I've come to appreciate more than compliments. I didn't "
        "expect a part-time job to teach me how to actually listen to strangers."
    ),
    "human_016": (
        "topic",
        "losing gracefully in chess club",
        "A seventh grader beat me at chess club in eleven moves, and I was "
        "furious about it for an embarrassingly long time. I replayed the game "
        "in my head for a week trying to find where I went wrong. Eventually I "
        "just asked him to show me, which felt humiliating and turned out to be "
        "the smartest thing I did all year. He's twelve. I'm sixteen. He still "
        "beats me more often than I'd like to admit, but now I ask him to "
        "explain it every time, and I've started doing the same for the kids "
        "newer than me."
    ),
}

# ---------------------------------------------------------------------------
# AI-style essays (development placeholders, hand-written imitations of
# generic LLM admissions-essay prose; NOT produced by calling any API)
# ---------------------------------------------------------------------------

AI_ESSAYS = {
    "ai_001": (
        "Write a compelling college admissions essay about leadership through "
        "student council in approximately 180 words.",
        "Leadership plays a pivotal role in shaping who I am today. Throughout "
        "my time on student council, I have consistently demonstrated a "
        "commitment to excellence and a passion for serving my peers. "
        "Furthermore, I learned to navigate the complexities of group "
        "decision-making, balancing diverse perspectives to achieve consensus. "
        "It is important to note that leadership is not about authority, but "
        "about empowering others to succeed. Moreover, organizing our school's "
        "annual charity drive taught me invaluable lessons about resilience and "
        "collaboration. In today's society, young leaders must be adaptable and "
        "empathetic. Additionally, I cultivated meaningful relationships with "
        "administrators and students alike, fostering a sense of unity within "
        "our community. These experiences have profoundly shaped my worldview "
        "and prepared me for the challenges ahead. In conclusion, my journey on "
        "student council has been a testament to the power of dedicated, "
        "compassionate leadership, and I am eager to bring these skills to your "
        "esteemed institution."
    ),
    "ai_002": (
        "Write a college admissions essay about resilience after academic "
        "setback in approximately 180 words.",
        "Resilience is a quality that has come to define my academic journey. "
        "When I received a disappointing grade on my chemistry midterm, I could "
        "have easily given up. Instead, I chose to delve into the underlying "
        "concepts I had failed to grasp. Moreover, this setback became a "
        "testament to my determination and work ethic. It is important to note "
        "that failure is not the opposite of success but an integral part of "
        "it. Furthermore, I sought help from my teacher during office hours, "
        "cultivating a deeper understanding of the material. Additionally, I "
        "developed a rigorous study schedule that I continue to use today. In "
        "today's society, students often fear failure rather than embracing it "
        "as a learning opportunity. This experience taught me to navigate the "
        "complexities of academic challenges with grace and perseverance. In "
        "conclusion, my ability to overcome this obstacle exemplifies the "
        "resilience I will bring to your campus community."
    ),
    "ai_003": (
        "Write a college admissions essay about community service abroad in "
        "approximately 180 words.",
        "My volunteer trip abroad was truly a transformative and eye-opening "
        "experience. Throughout my two weeks building homes with a local "
        "community, I gained an invaluable appreciation for cultural diversity. "
        "Moreover, this experience allowed me to delve into a way of life "
        "vastly different from my own. It is important to note that meaningful "
        "service requires humility rather than a savior complex. Furthermore, I "
        "formed genuine connections with the families we worked alongside, "
        "learning as much from them as I hope I contributed. Additionally, this "
        "journey was a testament to the power of global citizenship in today's "
        "society. I learned to navigate the complexities of working across "
        "language barriers with patience and creativity. These experiences have "
        "cultivated in me a lifelong commitment to service and cross-cultural "
        "understanding. In conclusion, this trip plays a pivotal role in how I "
        "envision my future contributions to any community I join."
    ),
    "ai_004": (
        "Write a college admissions essay about a passion for coding and STEM "
        "in approximately 180 words.",
        "From a young age, I have harbored a deep passion for computer science "
        "and technological innovation. Building my first mobile application "
        "allowed me to delve into the intricate world of software development. "
        "Moreover, this endeavor was a testament to countless hours of "
        "self-directed learning and problem-solving. It is important to note "
        "that coding, much like life, requires patience through inevitable "
        "bugs and failures. Furthermore, I joined my school's computer science "
        "club, where I could collaborate with like-minded peers who shared my "
        "enthusiasm. Additionally, I began mentoring younger students, "
        "cultivating their curiosity for STEM fields. In today's society, "
        "technology plays a pivotal role in solving humanity's greatest "
        "challenges. I have learned to navigate the complexities of algorithms "
        "and data structures with growing confidence. In conclusion, my passion "
        "for computer science has prepared me to make meaningful contributions "
        "to the ever-evolving landscape of technology."
    ),
    "ai_005": (
        "Write a college admissions essay about cultural identity and heritage "
        "in approximately 180 words.",
        "My cultural heritage is woven into the very tapestry of who I am as "
        "an individual. Growing up between two distinct traditions allowed me to "
        "delve into a rich and multifaceted identity. Moreover, celebrating both "
        "cultures' holidays taught me to appreciate diversity in today's "
        "society. It is important to note that identity is not static but "
        "constantly evolving through lived experience. Furthermore, my "
        "grandmother's stories about her homeland became a testament to "
        "resilience and perseverance across generations. Additionally, I have "
        "sought to navigate the complexities of belonging to multiple "
        "communities simultaneously. This duality plays a pivotal role in how I "
        "approach new challenges and relationships. I have cultivated a deep "
        "appreciation for the traditions that shaped my ancestors while forging "
        "my own unique path forward. In conclusion, my cultural heritage "
        "represents an invaluable tapestry of experiences that will enrich the "
        "diverse community at your university."
    ),
    "ai_006": (
        "Write a college admissions essay about environmental stewardship and "
        "a recycling club in approximately 180 words.",
        "Environmental stewardship plays a pivotal role in my vision for the "
        "future of our planet. As founder of my school's recycling initiative, I "
        "have had the opportunity to delve into sustainable practices firsthand. "
        "Moreover, this endeavor became a testament to the impact that grassroots "
        "action can have within a community. It is important to note that "
        "environmental change requires both individual responsibility and "
        "collective action. Furthermore, I organized monthly clean-up events "
        "that brought together students from diverse backgrounds. Additionally, "
        "I worked to navigate the complexities of school bureaucracy in order to "
        "secure funding for composting bins. In today's society, sustainability "
        "must be at the forefront of every institution's priorities. These "
        "experiences have cultivated in me an unwavering commitment to "
        "environmental advocacy. In conclusion, I am eager to continue this "
        "important work as a member of your campus community."
    ),
    "ai_007": (
        "Write a college admissions essay about teamwork learned through sports "
        "in approximately 180 words.",
        "Teamwork has consistently played a pivotal role throughout my athletic "
        "career. As captain of my varsity soccer team, I learned to delve into "
        "the dynamics of effective collaboration under pressure. Moreover, this "
        "leadership position was a testament to years of dedication and "
        "sacrifice. It is important to note that true teamwork requires "
        "sublimating individual glory for collective success. Furthermore, I "
        "worked to navigate the complexities of motivating teammates through "
        "difficult losing streaks. Additionally, I cultivated strong "
        "relationships with players of vastly different backgrounds and skill "
        "levels. In today's society, the ability to collaborate effectively is "
        "an invaluable and often underappreciated skill. These experiences on "
        "the field have shaped my approach to every group endeavor I undertake. "
        "In conclusion, the lessons I learned through athletics represent an "
        "invaluable foundation for future collaborative success."
    ),
    "ai_008": (
        "Write a college admissions essay about academic curiosity and a "
        "research project in approximately 180 words.",
        "Academic curiosity has always been the driving force behind my "
        "intellectual pursuits. Conducting an independent research project on "
        "local water quality allowed me to delve into the scientific method in "
        "a meaningful way. Moreover, this experience was a testament to the "
        "power of self-directed inquiry. It is important to note that genuine "
        "research requires embracing uncertainty and unexpected results. "
        "Furthermore, I had to navigate the complexities of data collection and "
        "statistical analysis largely on my own. Additionally, presenting my "
        "findings at the regional science fair cultivated my confidence as a "
        "communicator. In today's society, scientific literacy plays a pivotal "
        "role in addressing pressing environmental challenges. This project "
        "deepened my appreciation for the rigor and patience that authentic "
        "inquiry demands. In conclusion, my research experience has prepared me "
        "to contribute meaningfully to your institution's academic community."
    ),
    "ai_009": (
        "Write a college admissions essay about global citizenship and Model "
        "United Nations in approximately 180 words.",
        "Global citizenship plays a pivotal role in how I understand my "
        "responsibilities as a young leader. Through Model United Nations, I "
        "have had the opportunity to delve into complex international issues "
        "from diverse perspectives. Moreover, representing a foreign delegation "
        "was a testament to the importance of empathy in diplomacy. It is "
        "important to note that meaningful dialogue requires understanding "
        "viewpoints radically different from one's own. Furthermore, I learned "
        "to navigate the complexities of negotiation and compromise under "
        "significant time pressure. Additionally, this experience cultivated my "
        "passion for international relations and policy. In today's society, "
        "interconnected global challenges demand collaborative, cross-cultural "
        "solutions. These conferences have profoundly shaped my understanding of "
        "diplomacy and global interdependence. In conclusion, my commitment to "
        "global citizenship will be an invaluable asset to your university's "
        "international community."
    ),
    "ai_010": (
        "Write a college admissions essay about personal growth through "
        "failure in approximately 180 words.",
        "Failure, though painful in the moment, has become a testament to my "
        "personal growth over the years. When I was cut from the varsity "
        "basketball team, I had to delve into difficult questions about my own "
        "identity and worth. Moreover, this setback taught me that resilience "
        "is cultivated through adversity, not comfort. It is important to note "
        "that growth rarely happens without discomfort. Furthermore, I had to "
        "navigate the complexities of disappointment while supporting my "
        "teammates who made the roster. Additionally, this experience pushed me "
        "toward new pursuits I would never have otherwise discovered. In "
        "today's society, we often celebrate success while overlooking the "
        "invaluable lessons embedded in failure. This period of reflection "
        "plays a pivotal role in how I now approach every new challenge. In "
        "conclusion, I have come to view failure not as an endpoint, but as an "
        "essential step toward meaningful growth."
    ),
    "ai_011": (
        "Write a college admissions essay about the influence of a mentor in "
        "approximately 180 words.",
        "My mentor's guidance has played a pivotal role in shaping the person I "
        "have become. Under her tutelage, I was able to delve into subjects "
        "that had previously intimidated me. Moreover, her belief in my "
        "potential was a testament to the transformative power of mentorship. "
        "It is important to note that mentors do not simply provide answers; "
        "they cultivate independent thinking. Furthermore, she taught me to "
        "navigate the complexities of balancing ambition with self-compassion. "
        "Additionally, our weekly conversations helped me develop invaluable "
        "confidence in my own abilities. In today's society, meaningful "
        "mentorship relationships are increasingly rare and therefore especially "
        "precious. Her influence extended far beyond academics into how I "
        "approach relationships and challenges more broadly. In conclusion, the "
        "lessons instilled by my mentor represent a foundation I will carry "
        "throughout my collegiate journey and beyond."
    ),
    "ai_012": (
        "Write a college admissions essay about starting a small business in "
        "approximately 180 words.",
        "Entrepreneurship has allowed me to delve into the practical "
        "application of creativity and problem-solving. Starting a small "
        "business selling handmade candles was a testament to my willingness to "
        "take calculated risks. Moreover, this venture taught me to navigate "
        "the complexities of budgeting, marketing, and customer service "
        "simultaneously. It is important to note that entrepreneurial success "
        "requires resilience in the face of repeated setbacks. Furthermore, I "
        "had to cultivate relationships with local vendors and adapt my "
        "strategy based on customer feedback. Additionally, reinvesting profits "
        "into the business plays a pivotal role in my understanding of "
        "long-term financial planning. In today's society, young entrepreneurs "
        "must balance innovation with practical business fundamentals. This "
        "experience has been invaluable in developing my problem-solving and "
        "leadership abilities. In conclusion, my entrepreneurial journey has "
        "prepared me to pursue ambitious goals with confidence and resilience."
    ),
    "ai_013": (
        "Write a college admissions essay about social justice advocacy in "
        "approximately 180 words.",
        "Social justice advocacy plays a pivotal role in my vision for a more "
        "equitable future. Organizing a peaceful demonstration at my school "
        "allowed me to delve into the mechanics of grassroots activism. "
        "Moreover, this experience was a testament to the power of collective "
        "voice in effecting meaningful change. It is important to note that "
        "advocacy requires sustained commitment beyond a single event or "
        "moment. Furthermore, I had to navigate the complexities of building "
        "coalitions among students with differing viewpoints. Additionally, "
        "these efforts cultivated my understanding of systemic inequities "
        "within our education system. In today's society, young people "
        "increasingly recognize their power to drive institutional change. This "
        "work has deepened my commitment to lifelong advocacy and civic "
        "engagement. In conclusion, my experiences in social justice work "
        "represent an invaluable foundation for continued activism throughout "
        "my college career."
    ),
    "ai_014": (
        "Write a college admissions essay about artistic expression through "
        "painting in approximately 180 words.",
        "Painting has always allowed me to delve into emotions I struggle to "
        "articulate through words alone. Each canvas represents a testament to "
        "a particular season of my life and personal growth. Moreover, my art "
        "teacher encouraged me to navigate the complexities of abstract "
        "expression rather than rigid technical precision. It is important to "
        "note that artistic growth requires vulnerability and willingness to "
        "fail publicly. Furthermore, exhibiting my work at the community art "
        "show cultivated my confidence as a creative individual. Additionally, "
        "art plays a pivotal role in fostering empathy and cross-cultural "
        "understanding in today's society. I have come to view painting not "
        "merely as a hobby but as an invaluable form of self-discovery. These "
        "experiences have shaped how I approach creative and academic challenges "
        "alike. In conclusion, my passion for artistic expression will "
        "undoubtedly enrich the creative community at your institution."
    ),
    "ai_015": (
        "Write a college admissions essay about building technology for the "
        "local community in approximately 180 words.",
        "Technology plays a pivotal role in solving many of the challenges "
        "facing communities like mine. Building an app to connect local food "
        "banks with volunteers allowed me to delve into both technical and "
        "social problem-solving simultaneously. Moreover, this project was a "
        "testament to the potential of technology to drive meaningful, "
        "grassroots social change. It is important to note that effective "
        "solutions must be built in close collaboration with the communities "
        "they serve. Furthermore, I had to navigate the complexities of user "
        "feedback and iterative design under real-world constraints. "
        "Additionally, this experience cultivated invaluable skills in both "
        "software development and community engagement. In today's society, "
        "technologists have a responsibility to design with empathy and "
        "inclusion in mind. This project has profoundly shaped my aspirations "
        "for a career at the intersection of technology and public good. In "
        "conclusion, I hope to continue this important work at your university."
    ),
    "ai_016": (
        "Write a college admissions essay about a lifelong love of reading and "
        "learning in approximately 180 words.",
        "My lifelong love of reading has been a testament to the transformative "
        "power of literature. From an early age, books allowed me to delve into "
        "worlds and perspectives far beyond my own experience. Moreover, this "
        "passion for learning cultivated an insatiable intellectual curiosity "
        "that extends across every subject I encounter. It is important to note "
        "that reading is not merely an academic exercise but a lifelong journey "
        "of self-discovery. Furthermore, founding my school's book club allowed "
        "me to navigate the complexities of leading meaningful discussions among "
        "diverse peers. Additionally, literature plays a pivotal role in "
        "fostering empathy and critical thinking in today's society. These "
        "experiences have shaped my identity as both a reader and a thoughtful, "
        "engaged citizen. In conclusion, my enduring passion for reading and "
        "learning will undoubtedly enrich the intellectual community at your "
        "institution."
    ),
}

# ---------------------------------------------------------------------------
# Polished essays (development placeholders): a human essay, hand-rewritten
# in a more embellished, uniform, "AI-polished" register, while preserving
# the original facts/story. Manually authored, NOT produced via an API call.
# ---------------------------------------------------------------------------

POLISHED_ESSAYS = {
    "polished_001": (
        "human_001",
        "Falling in love with the scent of sawdust was not something I ever "
        "anticipated, yet that is precisely what occurred the summer I began "
        "assisting my grandfather in his garage. He would hand me a piece of "
        "scrap wood and simply instruct me to 'see what's in there,' an "
        "approach that initially frustrated me, as I craved clear instructions "
        "rather than open-ended riddles. My first birdhouse leaned dramatically, "
        "resembling something built in haste. He laughed warmly, declined to "
        "correct it for me, and encouraged me to try again with patience. By "
        "August, I had become the one urging him to slow down so I could "
        "properly finish a cut. That lopsided birdhouse still sits proudly on a "
        "shelf in my room, a testament to the value of patient learning."
    ),
    "polished_002": (
        "human_002",
        "My very first debate round concluded after a mere four minutes when I "
        "forgot my entire argument and stood frozen before the judge. It is "
        "important to note that the judge visibly set down her pen in "
        "disappointment. I wanted desperately to quit that very night, but my "
        "partner sent a single, powerful word: 'again.' Consequently, we "
        "dedicated ourselves to drilling rebuttals in her basement every Tuesday "
        "for an entire month. I continued to lose my next six rounds, yet by "
        "the regional tournament I could sense the argument forming even while "
        "my opponents were still speaking. Although we did not win the state "
        "championship, we advanced to the semifinal round, and I did not freeze "
        "once, which felt like a genuine testament to how far I had come."
    ),
    "polished_003": (
        "human_003",
        "My grandmother measures flour by hand rather than with a cup, and for "
        "years I found myself unable to replicate her bread no matter how "
        "diligently I tried. She would observe me kneading and simply shake her "
        "head with quiet disapproval. One memorable Sunday, she finally placed "
        "her hands over mine instead of offering further explanation, and "
        "something meaningful clicked into place that no recipe card could ever "
        "convey. Now, when relatives visit, I am the one preparing the dough "
        "while she critiques the crust from her chair with characteristic "
        "candor. In today's society, such traditions are increasingly rare. It "
        "is not truly about the bread itself; rather, it is the one time we are "
        "all quiet together in the same room, united by something timeless."
    ),
    "polished_004": (
        "human_004",
        "The first dog I encountered at the shelter bit through my glove, and I "
        "very nearly did not return the following Saturday. However, nobody "
        "there treated the incident as significant, so I resolved to show up "
        "regardless. Six months later, that very same dog, Biscuit, fell asleep "
        "with his head resting on my shoe during a quiet shift. I have cleaned "
        "more kennels than I can accurately count and have cried in the parking "
        "lot on two separate occasions when dogs found their forever homes, an "
        "emotional response that defies logic yet recurs every time. This "
        "experience has been a testament to the transformative power of "
        "compassion. I am no longer certain whether I am helping the shelter or "
        "whether the shelter is helping me."
    ),
    "polished_005": (
        "human_005",
        "I became physically ill before my very first guitar recital, a "
        "possibility nobody adequately warns you about beforehand. My hands "
        "trembled so severely during the introduction that I began a full step "
        "removed from everyone else. I desperately wanted to walk offstage. "
        "Instead, I simply stopped, looked toward my teacher seated in the "
        "front row, and courageously restarted. Nobody applauded, though "
        "nobody laughed either. Three recitals later, I still experience "
        "nervousness, but it has become the kind of nervousness that feels more "
        "like readiness than dread, a distinction that took me two full years to "
        "genuinely recognize and appreciate."
    ),
    "polished_006": (
        "human_006",
        "My family's restaurant operates with a single dishwasher, and for the "
        "majority of high school, that dishwasher was me. I once resented every "
        "Friday night shift while my friends enjoyed their evenings elsewhere. "
        "However, somewhere between the third and fourth summer, I began "
        "recognizing regulars by their orders before they even sat down, and my "
        "father started genuinely valuing my opinion on new menu additions. I "
        "still do not particularly enjoy washing dishes. Nevertheless, it is "
        "important to note that Mrs. Alvarez now requests me by name, and my "
        "father trusts me implicitly to close the restaurant independently, "
        "which plays a pivotal role in how I understand responsibility."
    ),
    "polished_007": (
        "human_007",
        "Our robot's arm snapped off a mere thirty seconds into the qualifying "
        "round, directly in front of the judge who had been the most critical of "
        "us throughout the season. My teammate wanted to cry, and honestly, so "
        "did I. We spent that entire night in a hotel bathroom armed with a hot "
        "glue gun and duct tape, attempting every conceivable solution. It held "
        "for precisely one more match, which was sufficient to avoid finishing "
        "last. We ultimately did not advance. Nevertheless, I learned more about "
        "torque, and about maintaining composure when something breaks in front "
        "of everyone, than from any match we had actually won, a testament to "
        "resilience under pressure."
    ),
    "polished_008": (
        "human_008",
        "I relocated here at eleven years old and comprehended perhaps one word "
        "out of every ten during my first English class. I would diligently "
        "write phrases phonetically in the back of my notebook simply to "
        "navigate lunch conversations successfully. My teacher, Ms. Reyes, "
        "permitted me to answer questions in writing before I could articulate "
        "them aloud, a small accommodation that proved profoundly significant. "
        "By eighth grade, I was translating for my mother during "
        "parent-teacher conferences. I continue to think in two languages "
        "depending on the subject matter, and I have stopped apologizing for "
        "the accent that emerges when I am fatigued, embracing it instead as "
        "part of my identity."
    ),
    "polished_009": (
        "human_009",
        "When my mother fell ill during my sophomore year, I began styling my "
        "little sister's hair each morning before school because nobody else "
        "was available to do so. I did not initially know how, resulting in "
        "numerous crooked braids and considerable tears, predominantly my own. "
        "She is seven years old now and proudly informs anyone who will listen "
        "that I create the best braids in the family, an assertion that is not "
        "entirely accurate but one I never correct. My mother has since "
        "recovered, yet I continue the hair routine most mornings, as we both "
        "quietly cherish the tradition we established during those difficult "
        "times, a testament to resilience within our family."
    ),
    "polished_010": (
        "human_010",
        "A stress fracture abruptly ended my sophomore cross country season "
        "three weeks before regionals, relegating me to watching from the "
        "sideline in a walking boot. This experience proved genuinely difficult "
        "to convey to individuals unfamiliar with running culture. Nevertheless, "
        "my coach insisted I maintain a training log throughout, documenting how "
        "I felt each day, even during periods of complete inactivity. When I "
        "finally returned to racing that spring, I was slower than I had ever "
        "been. I finished dead last in my first meet back, yet felt more "
        "genuine pride crossing that finish line than at any race preceding my "
        "injury, a powerful testament to perseverance."
    ),
    "polished_011": (
        "human_011",
        "My grandmother frequently missed her medication times, prompting me to "
        "develop a modest application over winter break that simply alerted her "
        "phone at the appropriate hours. My initial version crashed repeatedly "
        "and, on two occasions, sent notifications at three in the morning "
        "before I resolved the underlying bug. She continues to refer to it "
        "affectionately as 'the pill thing' and proudly demonstrates it to her "
        "neighbors as though it were magic, despite consisting of merely two "
        "hundred lines of code held together through patience and persistence. "
        "It is not particularly sophisticated. However, it represents the first "
        "creation of mine upon which another person genuinely depends, a "
        "testament to the meaningful impact of small innovations."
    ),
    "polished_012": (
        "human_012",
        "The vacant lot adjacent to our apartment building consisted solely of "
        "weeds and broken glass until three of us neighbors grew weary of the "
        "unsightly view. We possessed no genuine expertise and inadvertently "
        "killed most of our initial tomato plants through anxious "
        "overwatering. Mrs. Okafor from the third floor, it turned out, "
        "possessed extensive knowledge of soil composition and effectively "
        "became our unofficial instructor. Two summers later, the garden now "
        "sustains six families and has additionally become a space where "
        "neighbors genuinely converse, a transformation the lot never achieved "
        "as mere weeds. This endeavor plays a pivotal role in how I now "
        "understand the power of community-driven initiatives."
    ),
}


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def seed_human_essays() -> None:
    for essay_id, (_, topic, text) in HUMAN_ESSAYS.items():
        _write_text(HUMAN_DIR / f"{essay_id}.txt", text)
        _write_json(
            HUMAN_DIR / f"{essay_id}.json",
            {
                "category": "human",
                "topic": topic,
                "note": (
                    "Manually authored development placeholder essay. "
                    "Not a real applicant's admissions essay."
                ),
            },
        )


def seed_ai_essays() -> None:
    for essay_id, (prompt, text) in AI_ESSAYS.items():
        _write_text(AI_DIR / f"{essay_id}.txt", text)
        _write_json(
            AI_DIR / f"{essay_id}.json",
            {
                "category": "ai",
                "model": "development-placeholder",
                "prompt": prompt,
                "generated_at": GENERATED_AT,
                "note": (
                    "Hand-written imitation of generic AI-generated admissions-"
                    "essay prose. No external LLM API was called to produce this "
                    "text."
                ),
            },
        )


def seed_polished_essays() -> None:
    for essay_id, (source_id, text) in POLISHED_ESSAYS.items():
        source_text = HUMAN_ESSAYS[source_id][2]
        _write_text(POLISHED_DIR / f"{essay_id}.txt", text)
        _write_json(
            POLISHED_DIR / f"{essay_id}.json",
            {
                "category": "polished",
                "source_human_essay": f"{source_id}.txt",
                "model": "development-placeholder-manual-edit",
                "prompt": (
                    "Lightly polish the following college admissions essay for "
                    "grammar, flow, and word choice while preserving its "
                    "meaning and voice."
                ),
                "generated_at": GENERATED_AT,
                "note": (
                    "Hand-written stand-in for an LLM polish pass. No external "
                    "LLM API was called; generate_polished.py is the real "
                    "pipeline for when an API is configured."
                ),
            },
        )
        diff = sentence_diff(source_text, text)
        _write_json(POLISHED_DIR / f"{essay_id}.diff.json", diff)


def main() -> None:
    for d in (HUMAN_DIR, AI_DIR, POLISHED_DIR):
        d.mkdir(parents=True, exist_ok=True)

    seed_human_essays()
    seed_ai_essays()
    seed_polished_essays()

    print(f"Wrote {len(HUMAN_ESSAYS)} human essays to {HUMAN_DIR}")
    print(f"Wrote {len(AI_ESSAYS)} ai essays to {AI_DIR}")
    print(f"Wrote {len(POLISHED_ESSAYS)} polished essays to {POLISHED_DIR}")


if __name__ == "__main__":
    main()
