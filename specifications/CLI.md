Below is an updated specification for a command-line interface (CLI) tool called nugraph, reflecting the change that the tool should not accept a pre-existing blob URL. Instead, nugraph will:
	1.	Take a local file path from the user.
	2.	Upload that file to a storage bucket.
	3.	Retrieve and use the returned blob URL for the subsequent backend calls.

nugraph CLI Specification

1. Overview

nugraph is a command-line interface (CLI) that interacts with a backend system providing “Graph RAG” (Retrieval-Augmented Generation) capabilities. The CLI allows users to:
	1.	Authenticate against the backend service.
	2.	Upload a single file (locally) to the backend bucket.
	3.	Upload and index multiple files (locally) in one go.
	4.	Search the backend with a query string and receive relevant results.

Basic Command Structure

nugraph [command] [options] [arguments]

2. Commands

2.1. auth
	•	Description: Authenticates the user with the backend service.
	•	Usage:

nugraph auth [options]


	•	Arguments/Options:
	•	--username <USERNAME> or -u <USERNAME>: The username for authentication.
	•	--password <PASSWORD> or -p <PASSWORD>: The password for authentication.
	•	--config <FILE>: (Optional) Specifies a custom configuration file to store or read the auth token. Defaults to ~/.nugraph/config.json (or similar).
	•	Behavior:
	1.	Sends the provided credentials to the authentication endpoint.
	2.	On success, receives and stores an access token in a local configuration file or keychain.
	3.	Returns a success message or an error.
	•	Example:

nugraph auth -u alice -p secretpass



2.2. upload
	•	Description: Uploads a single local file to the storage bucket, obtains a blob URL, and sends that blob URL to the backend.
	•	Usage:

nugraph upload [options] <file_path>


	•	Arguments/Options:
	•	<file_path>: Required path to the file to be uploaded.
	•	--auth-token <TOKEN>: (Optional) Provide an auth token directly, overriding stored token.
	•	--output <FORMAT>: (Optional) Output format (e.g., json, text). Defaults to text.
	•	Behavior:
	1.	Reads the file from the specified <file_path>.
	2.	Sends the file data to the bucket (storage service).
	3.	Receives a blob URL from the storage service.
	4.	Passes this blob URL to the backend’s upload endpoint so that it can register or store metadata about the file.
	5.	Displays the blob URL (and any other info) to the user in the chosen output format.
	•	Example:

nugraph upload /path/to/document.pdf

Output (text):

Uploaded and registered file: https://storage.example.com/document1234



2.3. index
	•	Description: Uploads multiple local files at once, obtains their blob URLs, and indexes them with the backend.
	•	Usage:

nugraph index [options] <file_path_1> <file_path_2> ... <file_path_N>

or

nugraph index [options] --file <file_list>


	•	Arguments/Options:
	•	<file_path_*>: One or more local file paths that need to be uploaded.
	•	--file <FILE>: (Optional) A file containing a list of local file paths (one per line).
	•	--auth-token <TOKEN>: (Optional) Provide an auth token directly, overriding stored token.
	•	--output <FORMAT>: (Optional) Output format (e.g., json, text). Defaults to text.
	•	Behavior:
	1.	Accepts multiple local file paths (either directly or via a file).
	2.	For each file, uploads it to the bucket, obtains a blob URL.
	3.	Sends all blob URLs to the backend’s indexing endpoint in one request or in a loop.
	4.	Displays a success or error message along with any relevant data (e.g., how many files were uploaded and indexed successfully).
	•	Examples:
	1.	Passing file paths directly:

nugraph index ~/docs/doc1.pdf ~/docs/doc2.txt

	•	Internally uploads doc1.pdf and doc2.txt, gets blob URLs, and sends them to the backend for indexing.

	2.	Using a file list:

nugraph index --file my_file_list.txt

	•	my_file_list.txt might contain:

~/docs/doc1.pdf
~/docs/doc2.txt
~/reports/annual_summary.docx



2.4. search
	•	Description: Searches the indexed documents using a query string.
	•	Usage:

nugraph search [options] <query_string>


	•	Arguments/Options:
	•	<query_string>: Required query term or phrase.
	•	--auth-token <TOKEN>: (Optional) Provide an auth token directly, overriding stored token.
	•	--limit <N>: (Optional) Limit the number of results. Defaults to a server or CLI-defined value (e.g., 10).
	•	--output <FORMAT>: (Optional) Output format (e.g., json, text). Defaults to text.
	•	Behavior:
	1.	Sends the query string to the backend’s search endpoint.
	2.	Receives and displays the results in the specified format.
	•	Example:

nugraph search "how to configure my server"

Output (sample, json format):

[
  {
    "title": "Server Configuration Guide",
    "snippet": "This document explains how to configure your server..."
  },
  {
    "title": "Advanced Server Settings",
    "snippet": "Learn advanced server configuration options..."
  }
]

3. Authentication Flow
	1.	User runs nugraph auth -u <USERNAME> -p <PASSWORD>.
	2.	Tool sends the credentials to the auth endpoint (e.g., POST /auth).
	3.	Backend responds with an auth token (e.g., JWT or other token).
	4.	Tool stores the token in a local config file (default: ~/.nugraph/config.json) or in the system keychain.
	5.	Subsequent commands (e.g., upload, index, search) use the stored token.

Note: If a user passes --auth-token <TOKEN> explicitly, that token is used instead of the stored one.

4. Configuration & Environment
	•	Config File: By default, nugraph stores configuration data (e.g., auth token, CLI preferences) in ~/.nugraph/config.json.
	•	Environment Variables:
	•	NUGRAPH_API_URL: URL of the nugraph backend API (if not using a default).
	•	NUGRAPH_AUTH_TOKEN: Fallback token if no token is stored and none is provided via command line.
	•	NUGRAPH_CONFIG_FILE: Override the default config file location.

5. Error Handling
	•	Authentication Errors:
	•	If the token is invalid or expired, nugraph prompts the user to re-authenticate.
	•	File Upload Errors:
	•	If the file path is invalid or the upload fails, display an error message and a non-zero exit code.
	•	Indexing Errors:
	•	If any file upload fails, show an error.
	•	Search Errors:
	•	If the query string is missing, prompt the user for correct usage.
	•	If the backend returns an error, display the error message.

Error Codes might include:
	•	1 – General error
	•	2 – Authentication error
	•	3 – File not found or invalid path
	•	4 – Invalid input or missing arguments

6. Output Format
	•	text (default): Human-readable text.
	•	json: JSON-formatted data (particularly useful for scripts or other tooling).

Example:
	•	text output for nugraph upload /path/to/file.pdf:

Uploaded and registered file: https://storage.example.com/abc123


	•	json output:

{
  "status": "success",
  "blob_url": "https://storage.example.com/abc123"
}

7. Example Usage Scenarios
	1.	Authenticate:

nugraph auth -u alice -p secretpass

	•	Stores the token for later commands.

	2.	Upload a Single File:

nugraph upload /path/to/document.pdf

	•	Internally uploads document.pdf to the bucket, obtains a blob URL, then registers that blob URL with the nugraph backend.

	3.	Index Multiple Files:

nugraph index ~/docs/doc1.pdf ~/docs/doc2.txt ~/reports/annual_summary.docx

	•	Internally uploads all three files, obtains blob URLs, and passes them to the backend in one indexing request.

	4.	Search for Information:

nugraph search "how to configure my server" --limit 5 --output json

	•	Returns the top 5 results in JSON format.

8. Future Extensions
	•	Delete Command: A delete or remove subcommand that removes files from both the bucket and the nugraph index.
	•	Metadata Updates: A subcommand to update file metadata.
	•	Encryption: Optionally encrypting files during upload to the bucket.

Conclusion

This revised specification for the nugraph CLI tool outlines how to authenticate, upload single or multiple local files to a bucket (obtaining a blob URL), and then register those blob URLs with the backend. It also includes searching functionality, configuration details, error handling, and example scenarios to illustrate usage.