from landing.models import Page, PageElement
from mptt.models import MPTTModel

# Create page
page, created = Page.objects.get_or_create(
    title="Politi Suite",
    slug="politisuite",
    template="landing_basic.html"  # Наш шаблон
)
if created:
    print("Page created!")

# Функция для создания элемента (упрощает)
def create_element(page, type, content='', props={}, image=None, css_classes='', parent=None, order=0):
    elem, _ = PageElement.objects.get_or_create(
        page=page,
        type=type,
        content=content,
        props=props,
        image=image,
        css_classes=css_classes,
        parent=parent,
        order=order
    )
    elem.save()  # Для MPTT — перестраивает дерево
    return elem

# Root: Hero Container (container, order=0)
hero = create_element(page, 'container', css_classes='hero-section', order=0)
create_element(page, 'header', content='Politi Suite', props={'level': 1}, parent=hero, order=1)
create_element(page, 'text', content='Mastering Political Strategies', props={'level': 3}, parent=hero, order=2)  # h3 как text с props
create_element(page, 'text', content='Elevate Your Political Experience with', parent=hero, order=3)
create_element(page, 'header', content='Politi Suite', props={'level': 1}, parent=hero, order=4)
create_element(page, 'text', content='Are you ready to transform your political experience? Look no further! PolitiSuite is your go-to destination for exceptional suite of political tools that exceeds expectations.', parent=hero, order=5)

# Root: Why Choose Section (section, order=1)
why_section = create_element(page, 'section', css_classes='why-choose', order=1)
create_element(page, 'header', content='Why Choose PolitiSuite?', props={'level': 2}, parent=why_section, order=1)
why_list = create_element(page, 'list', props={'items': [
    {'text': 'Expertise: Our team of seasoned professionals brings years of experience in political tools. We understand the intricacies of political arena and deliver tailored solutions.'},
    {'text': 'Innovation: Stay ahead of the curve with our cutting-edge approaches. We pride ourselves on embracing the latest trends and technologies to provide you with unmatched suite of political tools.'},
    {'text': 'Client-Centric: Your satisfaction is our priority. We work closely with our clients to understand their unique needs, ensuring a personalized and seamless experience.'}
], 'ordered': False}, parent=why_section, order=2)

# Root: How We Can Help Section (section, order=2)
how_section = create_element(page, 'section', css_classes='how-we-help', order=2)
create_element(page, 'header', content='How We Can Help You', props={'level': 1}, parent=how_section, order=1)
create_element(page, 'text', content="Whether you're an organization or a political leader, we have the perfect PolitiSuite solution for you. Here's how we can help:", parent=how_section, order=2)
advanced_sub = create_element(page, 'section', css_classes='advanced-techniques', parent=how_section, order=3)
create_element(page, 'header', content='Advanced Campaign Techniques', props={'level': 2}, parent=advanced_sub, order=1)
create_element(page, 'text', content="At PolitiSuite, we redefine the art of political communication. Dive into the intricate world of political campaigns, communication triangles, and information flows with us. Our expertise encompasses a wide array of strategies, from navigating the war room to utilizing artificial intelligence for decision-making. Explore the nuances of political discourse, perception change, and campaign dynamics with PolitiSuite.", parent=advanced_sub, order=2)

# Root: Our Services Section (section, order=3) — с под-элементами
services_section = create_element(page, 'section', css_classes='our-services', order=3)
create_element(page, 'header', content='Our Services', props={'level': 1}, parent=services_section, order=1)

# Под-services (каждый как subsection с header + text, order по порядку)
services_data = [
    ("Communication Triangle", "Unravel the dynamics of communication involving sources, audiences and messaging. Explore how information flows within the triangle, shaping the discourse and influencing political outcomes"),
    ("Model of Information Flow in Political Campaigns", "Delve into our comprehensive model that dissects the complexities of information flow in political campaigns. From sources to messaging, we provide a nuanced understanding of the process."),
    ("War Room and Central Monitoring", "Witness the heart of political campaigns with our insights into war rooms and central monitoring. Learn how real-time analysis and strategic decisions shape the narrative."),
    ("Intelligence & Counterintelligence in Media Management", "Explore the intricate world of intelligence and counterintelligence in media management. Learn how IP detection combats illegal interventions, ensuring the integrity of the political discourse."),
    ("Negative Campaigns, Scandals, and Image Repair", "Navigate the delicate terrain of negative campaigns, scandals, and image repair. Understand how resilience plays a crucial role in shaping public perception."),
    ("AI in Campaign Monitoring and Decision Making", "Discover the role of artificial intelligence in monitoring campaigns and decision-making processes. Learn how data compiling and intention measurements shape effective political strategies."),
    ("Political Discourse Analysis and Persuasion", "Uncover the power of persuasion through political discourse analysis. Explore narratives, argumentation, and discursive nodes that influence voters' choices."),
    ("Microtargeting, Databases, and Data Analytics", "Master the art of microtargeting, leveraging databases of voters, and harnessing the power of data analytics. Understand how segmentation and predictive models optimize campaign effectiveness."),
    ("Funding, Volunteers, and Team Management", "Delve into the essentials of funding, cost per action, and generating votes. Learn effective team management strategies and the pivotal role of volunteers in successful political campaigns."),
    ("PACs, Canvas, and Voters Circles", "Explore the impact of Political Action Committees (PACs), canvasing, and creating voters circles. Understand the dynamics of targeting communities and building support."),
    ("The Campaign Plan and Political Agenda", "Craft a winning campaign plan and political agenda. Explore long-term and short-term factors that influence voters, ensuring a strategic and impactful campaign.")
]

for i, (title, desc) in enumerate(services_data, 1):
    sub_sec = create_element(page, 'section', parent=services_section, order=i)
    create_element(page, 'header', content=title, props={'level': 3}, parent=sub_sec, order=1)
    create_element(page, 'text', content=desc, parent=sub_sec, order=2)

# Root: Contact Text (text, order=4)
create_element(page, 'text', content="Ready to elevate your political strategies? Contact AZTech-ai today for unparalleled expertise in political campaigns, communication dynamics, organization and data-driven decision-making. Let's shape the future together.\n\n### Contact AZTech-ai for Your Political Information Needs", css_classes='contact-section', order=4)

print("All elements created! Check with: page.elements.root_nodes()")
