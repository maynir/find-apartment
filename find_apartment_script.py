#!/usr/bin/env python3

import facebook as fb
token = "EAAO55DH7N9cBAEjEypRzZCQ9oiZATwMUfGvsB0XSUL8phTuWG4jXTZCxuLs1uWenhbqxY9k22Ax8jnUQ5L2kvPU1MjE4t8OzCpkdskx9FfTehhletFP7owp0y7p4vTxq8SLqadN3NbrmKpkLZC5SmeztjGFvQ1DwEslJAuFbOfErZB3QCYOdmhZAZA2x0ZCdjCZADFEQZCqu4SVUA5JXyFBeKd0MUKPdwYHMwZA0RNq27UDHZADb3WJB0Dky"
graph_api = fb.GraphAPI(access_token=token)
print(graph_api.get_object("4936361429754534"))
# print(graph_api.get_object("4936361429754534"))
# fb_api = fb.
# print(fb_api.user.get_info(user_id="4936361429754534"))