# Overview
Content poster is an easy to setup\, fully functional Telegram bot that can find and post content to your channel built with [aiogram](https://github.com/aiogram/aiogram)\.
# Setup
 - Install latest python3 and its dependencies
 - Download and unzip the project
 - Install project packages via pip (`pip3 intall -r requirements.txt`)
 - Configure bot by editing `data.json` file
# Configuration
Configuration is made via editing `data.json` file\. You have already downloaded an example configuration\, here's a description of each parameter
### Service part
 - `integer` page \- Last used yande\.re page\, not recommended to edit \(defaults to `4000`\)
 - `string` token \- Bot token obtained from [@BotFather](https://t.me/BotFather)
 - `string` timezone \- Your [pytz timezone](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568) \(defaults to `"UTC"`\)
 - `bool` log_fills \- Whether to log post fillings or not \(defaults to `true`\)
 - `string` chat \- Chat ID where the bot will send posts
 - `bool` disable_config_check \- If you\'re risky enough you can disable configuration file validation passing true to this parameter \(defaults to `false`\)
### Posting part
 - `string` ratings \- List of post ratings to use\: explicit\, questionable\, safe\, \* \(defaults to `"*"`\)
- `list` post_time \- List of times when posts will be sent to your channel \(defaults to `["8:00", "12:00", "16:00", "20:00"]`\)
- `string` parse_mode \- Mode of parsing entities in captions can be HTML\, Markdown or MarkdownV2 \(defaults to `null`\)
- `string` caption \- Photo caption\, parse_mode will be applied \(defaults to `null`\)
- `bool` send_document - Whether to post document after photo \(defaults to `false`\)
- `string` document_name \- Name of document that will be posted after photo \(defaults to `"Document"`\)
- `string` document_caption \- Same as caption\, but for document

## Example `data.json`
```JSON
{
  "page": 4000,
  "ratings": "questionable, explicit",
  "post_time": [
    "8:00",
    "12:00",
    "16:00",
    "20:00"
  ],
  "timezone": "Europe\/Kiev",
  "token": "123456789:QWERTYUIOPASDFGHJKLZXCVBNMQWERTYUIO",
  "chat": -1001234567890,
  "caption": null,
  "parse_mode": "HTML",
  "send_document": true,
  "document_name": "Document",
  "document_caption": null,
  "log_fills": true,
  "disable_config_check": true
}
```
