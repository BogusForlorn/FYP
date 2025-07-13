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
