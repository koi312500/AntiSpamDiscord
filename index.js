const { Client, GatewayIntentBits } = require('discord.js');
const client = new Client({ intents: [ 
  GatewayIntentBits.DirectMessages,
  GatewayIntentBits.Guilds,
  GatewayIntentBits.GuildModeration,
  GatewayIntentBits.GuildMessages,
  GatewayIntentBits.MessageContent,] });

// discord 봇이 실행될 때 딱 한 번 실행할 코드를 적는 부분
client.once('ready', () => {
	console.log('Ready!');
});

// 디스코드 서버에 작성되는 모든 메시지를 수신하는 리스너
client.on('messageCreate', msg => {
	console.log(msg.content);
});

// 봇과 서버를 연결해주는 부분
client.login('Your_Token');