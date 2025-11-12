from SPARQLWrapper import SPARQLWrapper, POST, DIGEST
import pandas as pd
import os
import json
import requests
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

# GraphDB Configuration
GRAPHDB_ENDPOINT = 'http://localhost:7200/repositories/IModuleBuddy'
GRAPHDB_USERNAME = 'admin'
GRAPHDB_PASSWORD = 'root'

# Define custom namespaces
EX = Namespace("https://imodulebuddy.org/ontology#")
# The "SCHEMA" namespace definition has been removed as requested.

# Constants for CSV paths
CSV_DIRECTORY = os.path.join(os.getcwd(), 'csv')
SKILLS_CSV = os.path.join(CSV_DIRECTORY, 'skills.csv')
KNOWLEDGE_CSV = os.path.join(CSV_DIRECTORY, 'knowledge.csv')
OCCUPATIONS_CSV = os.path.join(CSV_DIRECTORY, 'occupations.csv')
LEARNING_OUTCOMES_CSV = os.path.join(CSV_DIRECTORY, 'learning_outcomes_uris.csv')
MODULES_CSV = os.path.join(CSV_DIRECTORY, 'modules.csv')
SCHEDULING_CSV = os.path.join(CSV_DIRECTORY, 'modules_scheduling.csv')
ASSESSMENTS_JSON = os.path.join(CSV_DIRECTORY, 'modules_assessments.json')


def get_sparql_wrapper():
    """Create and configure SPARQLWrapper instance"""
    sparql = SPARQLWrapper(GRAPHDB_ENDPOINT + '/statements')
    sparql.setHTTPAuth(DIGEST)
    sparql.setCredentials(GRAPHDB_USERNAME, GRAPHDB_PASSWORD)
    sparql.setMethod(POST)
    return sparql


def execute_sparql_update(query):
    """Execute SPARQL UPDATE query"""
    sparql = get_sparql_wrapper()
    sparql.setQuery(query)
    sparql.query()


def create_uri(base, identifier):
    """Create a URI for a resource"""
    # Clean identifier for URI usage
    clean_id = str(identifier).replace(' ', '_').replace('/', '_').replace('\\', '_')
    return URIRef(EX[clean_id])


def add_module(g, individual_name, module_link, module_title, module_description,
               module_type, module_comment, module_competency_to_be_achieved, module_content):
    """Add a module to the RDF graph"""
    module_uri = create_uri('module', individual_name)

    g.add((module_uri, RDF.type, EX.Module))
    g.add((module_uri, EX.individualName, Literal(individual_name)))
    g.add((module_uri, EX.moduleLink, Literal(module_link)))
    g.add((module_uri, EX.moduleTitle, Literal(module_title)))
    g.add((module_uri, EX.moduleDescription, Literal(module_description)))
    g.add((module_uri, EX.moduleType, Literal(module_type)))
    g.add((module_uri, EX.moduleComment, Literal(module_comment)))
    g.add((module_uri, EX.competencyToBeAchieved, Literal(module_competency_to_be_achieved)))
    g.add((module_uri, EX.moduleContent, Literal(module_content)))


def add_learning_outcome(g, learning_outcome, module_title):
    """Add a learning outcome to the RDF graph"""
    lo_uri = create_uri('learning_outcome', f"{module_title}_{learning_outcome[:50]}")

    g.add((lo_uri, RDF.type, EX.LearningOutcome))
    g.add((lo_uri, EX.learningOutcome, Literal(learning_outcome)))
    g.add((lo_uri, EX.moduleTitle, Literal(module_title)))


def add_skill(g, title, skill_type, index, description, uri):
    skill_uri = URIRef(uri)
    g.add((skill_uri, RDF.type, EX.Skill))
    g.add((skill_uri, EX["title"], Literal(title)))
    g.add((skill_uri, EX["type"], Literal(skill_type)))
    g.add((skill_uri, EX["index"], Literal(index)))
    g.add((skill_uri, EX["description"], Literal(description)))


def add_occupation(g, occupation, uri, description):
    """Add an occupation to the RDF graph"""
    occ_uri = URIRef(uri) if uri.startswith('http') else create_uri('occupation', uri)

    g.add((occ_uri, RDF.type, EX.Occupation))
    g.add((occ_uri, EX.occupation, Literal(occupation)))
    g.add((occ_uri, EX.uri, Literal(uri)))
    g.add((occ_uri, EX.description, Literal(description)))


def add_professor(g, professor_name, professor_surname):
    """Add a professor to the RDF graph"""
    import uuid
    prof_uuid = str(uuid.uuid4())
    prof_uri = create_uri('professor', prof_uuid)

    g.add((prof_uri, RDF.type, EX.Professor))
    g.add((prof_uri, EX.professorName, Literal(professor_name)))
    g.add((prof_uri, EX.professorSurname, Literal(professor_surname)))
    g.add((prof_uri, EX.uuid, Literal(prof_uuid)))

    return prof_uuid


def add_teaching_session(g, module, group_name, day, time, periodicity, semester, location, ay):
    """Add a teaching session to the RDF graph"""
    import uuid
    ts_uuid = str(uuid.uuid4())
    ts_uri = create_uri('teaching_session', ts_uuid)

    g.add((ts_uri, RDF.type, EX.TeachingSession))
    g.add((ts_uri, EX.module, Literal(module)))
    g.add((ts_uri, EX.groupName, Literal(group_name)))
    g.add((ts_uri, EX.day, Literal(day)))
    g.add((ts_uri, EX.time, Literal(time)))
    g.add((ts_uri, EX.periodicity, Literal(periodicity)))
    g.add((ts_uri, EX.semester, Literal(semester)))
    g.add((ts_uri, EX.location, Literal(location)))
    g.add((ts_uri, EX.ay, Literal(ay)))
    g.add((ts_uri, EX.uuid, Literal(ts_uuid)))

    return ts_uuid


def link_module_teaching_session(g, module_name, teaching_session_uuid):
    """Link a module to a teaching session"""
    module_uri = create_uri('module', module_name)
    ts_uri = create_uri('teaching_session', teaching_session_uuid)

    g.add((module_uri, EX.hasSchedule, ts_uri))


def link_teaching_session_professor(g, teaching_session_uuid, professor_uuid):
    """Link a teaching session to a professor"""
    ts_uri = create_uri('teaching_session', teaching_session_uuid)
    prof_uri = create_uri('professor', professor_uuid)

    g.add((ts_uri, EX.taughtBy, prof_uri))


def link_occupation_skill(g, occupation_uri, skill_uri, relation_type):
    """Link an occupation to a skill"""
    occ_uri = URIRef(occupation_uri) if occupation_uri.startswith('http') else create_uri('occupation', occupation_uri)
    skill_uri_ref = URIRef(skill_uri) if skill_uri.startswith('http') else create_uri('skill', skill_uri)

    g.add((occ_uri, EX.requiresSkill, skill_uri_ref))
    # Add relation type as a reified statement or property
    g.add((occ_uri, EX[f'requiresSkill_{relation_type}'], skill_uri_ref))


def link_module_learning_outcome(g, module_name, learning_outcome):
    """Link a module to a learning outcome"""
    module_uri = create_uri('module', module_name)
    lo_uri = create_uri('learning_outcome', f"{module_name}_{learning_outcome[:50]}")

    g.add((module_uri, EX.hasLearningOutcome, lo_uri))


def link_learning_outcome_skill(g, module_title, learning_outcome, skill_uri):
    """Link a learning outcome to a skill"""
    lo_uri = create_uri('learning_outcome', f"{module_title}_{learning_outcome[:50]}")
    skill_uri_ref = URIRef(skill_uri) if skill_uri.startswith('http') else create_uri('skill', skill_uri)

    g.add((lo_uri, EX.hasSkill, skill_uri_ref))


def process_occupation_skill_link(g, df):
    """Process occupation-skill relationships from dataframe"""
    for _, r in df.iterrows():
        if pd.notna(r['essential_skills']):
            essential_skills = r['essential_skills'].split(',')
            for skill_uri in essential_skills:
                link_occupation_skill(g, r['uri'], skill_uri.strip(), 'essential')

        if pd.notna(r['essential_knowledge']):
            essential_knowledge = r['essential_knowledge'].split(',')
            for knowledge_uri in essential_knowledge:
                link_occupation_skill(g, r['uri'], knowledge_uri.strip(), 'essential')

        if pd.notna(r['optional_skills']):
            optional_skills = r['optional_skills'].split(',')
            for skill_uri in optional_skills:
                link_occupation_skill(g, r['uri'], skill_uri.strip(), 'optional')

        if pd.notna(r['optional_knowledge']):
            optional_knowledge = r['optional_knowledge'].split(',')
            for knowledge_uri in optional_knowledge:
                link_occupation_skill(g, r['uri'], knowledge_uri.strip(), 'optional')


def process_module_learning_outcome_link(g, df):
    """Process module-learning outcome relationships from dataframe"""
    for _, r in df.iterrows():
        module_title = r['Module Title']
        learning_outcome = r['Learning Outcome']
        link_module_learning_outcome(g, module_title, learning_outcome)


def process_learning_outcome_skill_link(g, df):
    """Process learning outcome-skill relationships from dataframe"""
    for _, r in df.iterrows():
        module_title = r['Module Title']
        learning_outcome = r['Learning Outcome']

        if pd.notna(r['Promoted skill']):
            skills_uris = r['Promoted skill'].split(',')
            for uri in skills_uris:
                link_learning_outcome_skill(g, module_title, learning_outcome, uri.strip())

        if pd.notna(r['Promoted knowledge']):
            knowledge_uris = r['Promoted knowledge'].split(',')
            for uri in knowledge_uris:
                link_learning_outcome_skill(g, module_title, learning_outcome, uri.strip())


def update_modules_with_assessment_info(g):
    """Update modules with assessment information"""
    with open(ASSESSMENTS_JSON, 'r', encoding='utf-8') as f:
        assessment_data = json.load(f)

    for entry in assessment_data:
        module_name = entry['module_name']
        module_uri = create_uri('module', module_name)

        g.add((module_uri, EX.projectWork, Literal(entry['project_work'], datatype=XSD.boolean)))
        g.add((module_uri, EX.assessmentType, Literal(entry['assessment_type'])))
        g.add((module_uri, EX.oralAssessment, Literal(entry['oral_assessment'], datatype=XSD.boolean)))


def upload_to_graphdb(g):
    """Upload RDF graph to GraphDB"""
    ttl_data = g.serialize(format='turtle')

    headers = {
        'Content-Type': 'text/turtle'
    }

    response = requests.post(
        GRAPHDB_ENDPOINT + '/statements',
        data=ttl_data.encode('utf-8'),
        headers=headers,
        auth=(GRAPHDB_USERNAME, GRAPHDB_PASSWORD)
    )

    if response.status_code in (200, 204):
        print("✅ Data uploaded to GraphDB successfully!")
    else:
        print("❌ Failed to upload data.")
        print("Status:", response.status_code)
        print("Response:", response.text)


def populate_graph():
    """Main function to populate the graph"""
    # Create RDF graph
    g = Graph()
    g.bind('ex', EX)

    # This line was changed as requested.
    # It binds the prefix 'schema:' to the RDF namespace.
    g.bind('schema', RDF)

    print("Loading skills...")
    skills_df = pd.read_csv(SKILLS_CSV)
    for _, row in skills_df.iterrows():
        add_skill(g, row['title'], 'skill', row['index'], row['description'], row['uri'])

    print("Loading knowledge...")
    knowledge_df = pd.read_csv(KNOWLEDGE_CSV)
    for _, row in knowledge_df.iterrows():
        add_skill(g, row['title'], 'knowledge', row['index'], row['description'], row['uri'])

    print("Loading occupations...")
    occupations_df = pd.read_csv(OCCUPATIONS_CSV)
    for _, row in occupations_df.iterrows():
        add_occupation(g, row['occupation'], row['uri'], row['description'])

    print("Loading learning outcomes...")
    learning_outcomes_df = pd.read_csv(LEARNING_OUTCOMES_CSV)
    for _, row in learning_outcomes_df.iterrows():
        add_learning_outcome(g, row['Learning Outcome'], row['Module Title'])

    print("Loading modules...")
    modules_df = pd.read_csv(MODULES_CSV)
    for _, row in modules_df.iterrows():
        course_comment = row['Course_Comment'] if pd.notna(row['Course_Comment']) else ""
        add_module(g, row['Individual Name'], row['Course_Link'], row['Course_Title'],
                   row['Course_Description'], row['Course_Type'], course_comment,
                   row['Course_Competency_to_be_achieved'], row['Course_Content'])

    print("Creating relationships...")
    process_module_learning_outcome_link(g, learning_outcomes_df)
    process_learning_outcome_skill_link(g, learning_outcomes_df)
    process_occupation_skill_link(g, occupations_df)

    print("Loading scheduling and professors...")
    scheduling_df = pd.read_csv(SCHEDULING_CSV, skipinitialspace=True)
    for _, row in scheduling_df.iterrows():
        teaching_session_uuid = add_teaching_session(
            g,
            module=row['Individual Name'],
            group_name=row['Group_Name'],
            day=row['Day'],
            time=row['Time'],
            periodicity=row['Periodicity'],
            semester=row['Semester'],
            location=row['Location'],
            ay=row['AY']
        )

        link_module_teaching_session(g, module_name=row['Individual Name'],
                                     teaching_session_uuid=teaching_session_uuid)

        professor_uuid = add_professor(g,
                                       professor_name=row['Professor_Name'],
                                       professor_surname=row['Professor_Surname'])

        link_teaching_session_professor(g,
                                        teaching_session_uuid=teaching_session_uuid,
                                        professor_uuid=professor_uuid)

    print("Adding assessment information...")
    update_modules_with_assessment_info(g)

    print(f"Total triples created: {len(g)}")
    print("Uploading to GraphDB...")
    upload_to_graphdb(g)


def main():
    """Main entry point for populating the graph"""
    print("=" * 60)
    print("GraphDB Population Script")
    print("=" * 60)

    try:
        populate_graph()
        print("\n" + "=" * 60)
        print("✓ SUCCESS: Graph populated successfully!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ ERROR: Failed to populate graph")
        print(f"Error details: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()