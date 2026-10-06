from google.genai import types

SEARCH_NOTES_DECLARATION = types.FunctionDeclaration(
    name="search_notes",
    description="Search the user's notes by keyword/semantic relevance. Returns matching notes with id and a text snippet.",
    parameters_json_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "What to search for"},
            "top_k": {"type": "integer", "description": "Max results to return"},
        },
        "required": ["query"],
    },
)

GET_NOTE_DECLARATION = types.FunctionDeclaration(
    name="get_note",
    description="Fetch the full title and body of one specific note by its id.",
    parameters_json_schema={
        "type": "object",
        "properties": {"note_id": {"type": "string", "description": "The note's id, from search_notes"}},
        "required": ["note_id"],
    },
)

DELETE_NOTE_DECLARATION = types.FunctionDeclaration(
    name="delete_note",
    description="Permanently delete one note. Always call this when the user asks to delete something — the system itself handles pausing for human approval, you don't need to ask permission in text.",
    parameters_json_schema={
        "type": "object",
        "properties": {"note_id": {"type": "string", "description": "The note's id to delete"}},
        "required": ["note_id"],
    },
)

CREATE_NOTE_DECLARATION = types.FunctionDeclaration(
    name="create_note",
    description="Create a new note with the given title and body.",
    parameters_json_schema={
        "type": "object",
        "properties": {"title": {"type": "string"}, "body": {"type": "string"}},
        "required": ["title", "body"],
    },
)

UPDATE_NOTE_DECLARATION = types.FunctionDeclaration(
    name="update_note",
    description="Overwrite an existing note's title and body. DESTRUCTIVE and irreversible — call get_note first to see current content before proposing changes.",
    parameters_json_schema={
        "type": "object",
        "properties": {"note_id": {"type": "string"}, "title": {"type": "string"}, "body": {"type": "string"}},
        "required": ["note_id", "title", "body"],
    },
)

BULK_DELETE_NOTES_DECLARATION = types.FunctionDeclaration(
    name="bulk_delete_notes",
    description="Permanently delete multiple notes at once. DESTRUCTIVE — requires a single human approval covering the whole batch.",
    parameters_json_schema={
        "type": "object",
        "properties": {"note_ids": {"type": "array", "items": {"type": "string"}, "description": "ids of all notes to delete"}},
        "required": ["note_ids"],
    },
)