# PenAI 
The heuristic penetration testing tool that integrates an LLM into the workflow by interfacing an LLM to invoke commands and adjusting according.
You will need an OpenAI API key to run this tool. _if you don't have one, reach out to Borgor. He paid 5 USD for the API._


I haven't gotten around to making the script to setup. Just do the following to setup:
```
npm install openai dotenv
#and other python libraries idk u can tell how last minute this is because I haven't gotten the time to test on another machine
export OPENAI_API_KEY="sk-proj-<YOUR KEY HERE>"
```

In another terminal, launch your ZAP Proxy daemon:
```
zaproxy -daemon -config 'api.addrs.addr.name=.*' -config api.addrs.addr.regex=true -port 8080
```

If you haven't got a vulnerable web application to test on, you can refer to my other repo for a simple, lightweight server you can use (https://github.com/BogusForlorn/vulnerable_web)


I've run into a lot of issues developing and debugging this project. If you face the following issues, you can do:
Unable to run node files
```
npm init -y
```

SSL log key file not functioning
```
unset SSLKEYLOGFILE
```


If you see an error like:
```
file:///home/kali/FYP1/node_modules/openai/index.mjs:48
            throw new Errors.OpenAIError("The OPENAI_API_KEY environment variable is missing or empty; either provide it, or instantiate the OpenAI client with an apiKey option, like new OpenAI({ apiKey: 'My API Key' }).");
                  ^

OpenAIError: The OPENAI_API_KEY environment variable is missing or empty; either provide it, or instantiate the OpenAI client with an apiKey option, like new OpenAI({ apiKey: 'My API Key' }).
    at new OpenAI (file:///home/kali/FYP1/node_modules/openai/index.mjs:48:19)
    at file:///home/kali/FYP1/chatgpt_wrapper.js:7:16
    at ModuleJob.run (node:internal/modules/esm/module_job:263:25)
    at async ModuleLoader.import (node:internal/modules/esm/loader:540:24)
    at async asyncRunEntryPointWithESMLoader (node:internal/modules/run_main:117:5)
```
Reach out to borgor for the OpenAI API key
