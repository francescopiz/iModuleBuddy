import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
import re

class GraphDbMethods:
    def __init__(self):
        """Initialize the connection to the GraphDB repository."""
        self.endpoint = st.secrets["GRAPHDB_ENDPOINT"]
        self.username = st.secrets["GRAPHDB_USERNAME"]
        self.password = st.secrets["GRAPHDB_PASSWORD"]

        self.sparql = SPARQLWrapper(self.endpoint)
        self.sparql.setCredentials(self.username, self.password)
        self.sparql.setReturnFormat(JSON)

        # Updated prefixes to match your data loading script and request
        self.prefixes = """
            PREFIX ex: <https://imodulebuddy.org/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        """

    # ----------------------------- #
    # Generic query helpers
    # ----------------------------- #
    def query(self, query_str):
        """Execute a SPARQL SELECT query."""
        self.sparql.setQuery(self.prefixes + query_str)
        results = self.sparql.query().convert()
        return results["results"]["bindings"]

    def update(self, query_str):
        """Execute a SPARQL UPDATE query (INSERT/DELETE)."""
        self.sparql.setMethod("POST")
        self.sparql.setQuery(self.prefixes + query_str)
        self.sparql.query()
        self.sparql.setMethod("GET")  # Reset

    # ----------------------------- #
    # Data retrieval methods
    # ----------------------------- #

    def get_modules(self):
        query = """
        SELECT ?module_title
        WHERE {
          ?m a ex:Module ;
             ex:moduleTitle ?module_title .
        }
        ORDER BY ?module_title
        """
        results = self.query(query)
        return [r["module_title"]["value"] for r in results]

    def get_occupations(self):
        query = """
        SELECT ?occupation
        WHERE {
          ?o a ex:Occupation ;
             ex:occupation ?occupation .
        }
        ORDER BY ?occupation
        """
        results = self.query(query)
        return [r["occupation"]["value"] for r in results]

    def get_professors(self):
        query = """
        SELECT DISTINCT ?fullname
        WHERE {
          ?p a ex:Professor ;
             ex:professorName ?first ;
             ex:professorSurname ?last .
          BIND(CONCAT(?first, " ", ?last) AS ?fullname)
        }
        ORDER BY ?fullname
        """
        results = self.query(query)
        return [r["fullname"]["value"] for r in results]

    def get_module_overview(self):
        query = """
        SELECT ?title ?type
        WHERE {
          ?m a ex:Module ;
             ex:moduleTitle ?title ;
             ex:moduleType ?type .
        }
        """
        results = self.query(query)
        return [
            {
                "module": {
                    "module_title": r["title"]["value"],
                    "module_type": r["type"]["value"],
                },
                "score": 0,
            }
            for r in results
        ]

    def get_modules_by_occupation(self, occupation):
        # This query now correctly joins through LearningOutcomes to find skills
        query = f"""
        SELECT ?module_title ?skill_title ?occupation_name
        WHERE {{
          ?o a ex:Occupation ;
             ex:occupation "{occupation}" ;
             ex:requiresSkill ?skill .
          ?skill ex:title ?skill_title .

          ?m a ex:Module ;
             ex:moduleTitle ?module_title ;
             ex:hasLearningOutcome ?lo .
          ?lo ex:hasSkill ?skill .

          ?o ex:occupation ?occupation_name .
        }}
        ORDER BY ?module_title
        """
        results = self.query(query)
        return [
            {
                "module_title": r["module_title"]["value"],
                "skill": r["skill_title"]["value"],
                "occupation": r["occupation_name"]["value"],
            }
            for r in results
        ]

    def get_teaching_sessions_by_modules(self, modules):
        """Get teaching sessions linked to modules."""
        if not modules:
            return []
        values = " ".join([f'"{m}"' for m in modules])
        query = f"""
        SELECT ?module_title ?ay ?day ?group ?location ?periodicity ?semester ?time
        WHERE {{
          ?m a ex:Module ;
             ex:moduleTitle ?module_title ;
             ex:hasSchedule ?ts .
          ?ts ex:ay ?ay ;
              ex:day ?day ;
              ex:groupName ?group ;
              ex:location ?location ;
              ex:periodicity ?periodicity ;
              ex:semester ?semester ;
              ex:time ?time .
          FILTER(?module_title IN ({values}))
        }}
        ORDER BY ?module_title
        """
        results = self.query(query)

        # Grouping results by module_title
        module_sessions = {}
        for r in results:
            title = r["module_title"]["value"]
            if title not in module_sessions:
                module_sessions[title] = {
                    "module_title": title,
                    "teaching_session": []
                }

            module_sessions[title]["teaching_session"].append({
                "ay": r["ay"]["value"],
                "day": r["day"]["value"],
                "group_name": r["group"]["value"],
                "location": r["location"]["value"],
                "periodicity": r["periodicity"]["value"],
                "semester": r["semester"]["value"],
                "time": r["time"]["value"],
            })

        return list(module_sessions.values())

    def get_filtered_modules(self):
        """Return all modules excluding thesis-related ones."""
        all_modules = self.get_modules()
        exclude = {
            "Research Methods in Information Systems",
            "Master Thesis",
            "Master Thesis Proposal",
        }
        return [m for m in all_modules if m not in exclude]

    def get_extra_modules(self):
        """Return thesis-related modules."""
        query = """
        SELECT ?module_title ?type
        WHERE {
          ?m a ex:Module ;
             ex:moduleTitle ?module_title ;
             ex:moduleType ?type .
          FILTER(?module_title IN (
            "Research Methods in Information Systems",
            "Master Thesis",
            "Master Thesis Proposal"
          ))
        }
        """
        results = self.query(query)
        return [
            {"module_title": r["module_title"]["value"], "module_type": r["type"]["value"]}
            for r in results
        ]

    # ----------------------------- #
    # Filters & Matching
    # ----------------------------- #

    def matches_lecturer(self, module_title, lecturer):
        query = f"""
        ASK {{
          ?m a ex:Module ;
             ex:moduleTitle "{module_title}" ;
             ex:hasSchedule ?ts .
          ?ts ex:taughtBy ?prof .
          ?prof ex:professorSurname ?surname .
          FILTER(CONTAINS(LCASE("{lecturer}"), LCASE(?surname)))
        }}
        """
        self.sparql.setQuery(self.prefixes + query)
        return self.sparql.query().convert()["boolean"]

    def matches_day(self, module_title, day):
        query = f"""
        ASK {{
          ?m a ex:Module ;
             ex:moduleTitle "{module_title}" ;
             ex:hasSchedule ?ts .
          ?ts ex:day "{day}" .
        }}
        """
        self.sparql.setQuery(self.prefixes + query)
        return self.sparql.query().convert()["boolean"]

    def matches_assessment_type(self, module_title, assessment_type):
        query = f"""
        ASK {{
          ?m a ex:Module ;
             ex:moduleTitle "{module_title}" ;
             ex:assessmentType ?type .
          FILTER(LCASE(?type) = LCASE("{assessment_type}"))
        }}
        """
        self.sparql.setQuery(self.prefixes + query)
        return self.sparql.query().convert()["boolean"]

    def has_project_work(self, module_title):
        query = f"""
        ASK {{
          ?m a ex:Module ;
             ex:moduleTitle "{module_title}" ;
             ex:projectWork true .
        }}
        """
        self.sparql.setQuery(self.prefixes + query)
        return self.sparql.query().convert()["boolean"]

    def has_oral_assessment(self, module_title):
        query = f"""
        ASK {{
          ?m a ex:Module ;
             ex:moduleTitle "{module_title}" ;
             ex:oralAssessment true .
        }}
        """
        self.sparql.setQuery(self.prefixes + query)
        return self.sparql.query().convert()["boolean"]

    # ----------------------------------------------------------------- #
    # NEWLY TRANSLATED METHOD
    # ----------------------------------------------------------------- #

    def get_modules_by_preferences(
            self,
            taken_modules,
            desired_lecturers,
            available_days,
            assessment_type,
            project_work,
            oral_assessment
    ):
        """
        Fetches modules based on a scoring of user preferences.
        This is the SPARQL equivalent of the provided Cypher query.
        """

        # --- 1. Build Filter Blocks for SPARQL ---

        # Filter: Taken Modules (List of module titles)
        taken_modules_filter = ""
        if taken_modules:
            taken_values = ", ".join([f'"{m}"' for m in taken_modules])
            taken_modules_filter = f"FILTER(?module_title NOT IN ({taken_values}))"

        # Score: Available Days (List of strings)
        day_bind_str = "BIND(0 AS ?day_match_score)"
        if available_days:
            # Create a regex like "(Monday|Tuesday|Friday)"
            day_regex = "|".join([re.escape(d) for d in available_days])
            day_bind_str = f"""
                BIND(IF(BOUND(?days_str) && REGEX(?days_str, "{day_regex}", "i"), 1, 0) AS ?day_match_score)
            """

        # Score: Desired Lecturers (List of strings)
        # Checks if any desired lecturer name (e.g., "Prof. Smith")
        # CONTAINS any of the module's professor surnames (e.g., "Smith")
        lecturer_bind_str = "BIND(0 AS ?lecturer_match_score)"
        if desired_lecturers:
            # Create a check for each desired lecturer
            # e.g., REGEX(LCASE("Prof. Adam Smith"), LCASE("Smith|Jones|Miller"), "i")
            lecturer_checks = [
                f'REGEX(LCASE("{re.escape(lec)}"), LCASE(?surnames_str), "i")'
                for lec in desired_lecturers
            ]
            lecturer_filter_str = " || ".join(lecturer_checks)

            lecturer_bind_str = f"""
                BIND(IF(BOUND(?surnames_str) && ?surnames_str != "" && ({lecturer_filter_str}), 1, 0) AS ?lecturer_match_score)
            """

        # Score: Assessment Type (String)
        assessment_bind_str = "BIND(0 AS ?assessment_match_score)"
        if assessment_type:
            assessment_type_lower = assessment_type.lower()
            if assessment_type_lower == "individual_and_group":
                assessment_bind_str = 'BIND(IF(BOUND(?assessment_type_prop) && LCASE(STR(?assessment_type_prop)) IN ("individual", "group", "individual_and_group"), 1, 0) AS ?assessment_match_score)'
            else:
                assessment_bind_str = f'BIND(IF(BOUND(?assessment_type_prop) && LCASE(STR(?assessment_type_prop)) = "{assessment_type_lower}", 1, 0) AS ?assessment_match_score)'

        # Score: Project Work (Boolean)
        project_work_bool = str(project_work).lower()
        project_bind_str = f'BIND(IF(BOUND(?project_work_prop) && ?project_work_prop = {project_work_bool}, 1, 0) AS ?project_work_match_score)'

        # Score: Oral Assessment (Boolean)
        oral_assessment_bool = str(oral_assessment).lower()
        oral_bind_str = f'BIND(IF(BOUND(?oral_assessment_prop) && ?oral_assessment_prop = {oral_assessment_bool}, 1, 0) AS ?oral_assessment_match_score)'

        # --- 2. Construct the Full SPARQL Query ---

        query_str = f"""
        SELECT ?module_title ?module_type ?preference_score
        WHERE {{
            # --- Outer select: Calculate final score ---
            SELECT ?module_title ?module_type 
                   ( (?day_match_score) + 
                     (?lecturer_match_score) + 
                     (?assessment_match_score) + 
                     (?project_work_match_score) + 
                     (?oral_assessment_match_score) 
                   AS ?preference_score)
            WHERE {{
                # --- Inner select: Get all modules and their properties/aggregates ---
                SELECT ?m ?module_title ?module_type
                       (GROUP_CONCAT(DISTINCT ?day; separator="|") AS ?days_str)
                       (GROUP_CONCAT(DISTINCT ?surname; separator="|") AS ?surnames_str)
                       ?assessment_type_prop ?project_work_prop ?oral_assessment_prop
                WHERE {{
                    ?m a ex:Module ;
                       ex:moduleTitle ?module_title ;
                       ex:moduleType ?module_type .

                    # Optional properties for scoring
                    OPTIONAL {{ ?m ex:assessmentType ?assessment_type_prop . }}
                    OPTIONAL {{ ?m ex:projectWork ?project_work_prop . }}
                    OPTIONAL {{ ?m ex:oralAssessment ?oral_assessment_prop . }}

                    # Optional schedule info
                    OPTIONAL {{
                        ?m ex:hasSchedule ?ts .
                        OPTIONAL {{ ?ts ex:day ?day . }}
                        OPTIONAL {{
                            ?ts ex:taughtBy ?prof .
                            ?prof a ex:Professor ;
                                   ex:professorSurname ?surname .
                        }}
                    }}

                    # Filter out taken modules
                    {taken_modules_filter}
                }}
                GROUP BY ?m ?module_title ?module_type ?assessment_type_prop ?project_work_prop ?oral_assessment_prop
                # --- End Inner select ---

                # --- Calculate individual scores (0 or 1) ---
                {day_bind_str}
                {lecturer_bind_str}
                {assessment_bind_str}
                {project_bind_str}
                {oral_bind_str}
            }}
        }}
        ORDER BY DESC(?preference_score)
        """

        # --- 3. Execute Query and Format Results ---
        try:
            results = self.query(query_str)
            return [
                {
                    "module": {
                        "module_title": r["module_title"]["value"],
                        "module_type": r["module_type"]["value"]
                    },
                    # Convert score from string literal to integer
                    "preference_score": int(r["preference_score"]["value"])
                }
                for r in results
            ]
        except Exception as e:
            print(f"Error executing preference query: {e}")
            print(f"Query: {self.prefixes + query_str}")
            return []