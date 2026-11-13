const userData = [
  {
    id: 1,
    name: 'test',
    api_token: 'test',
    followers: [
      {
        id: 2,
      }
    ],
    following: [
      {
        id: 2,
      }
    ]
  },
  {
    id: 2,
    name: 'test2',
    api_token: 'test2',
    followers: [
      {
        id: 1,
      }
    ],
    following: [
      {
        id: 1,
      }
    ]
  },
]

export const users = [
  userData[0],
  userData[1],
]

export const userOneAuthInfo = {
  username: userData[0].username,
  password: userData[0].password
}

export const tweets = [{
  id: 'sone',
  content: 'text',
  author: {
    id: "some",
    name: 'Vaame'
  },
  attachments: [
    'https://s5o.ru/storage/dumpster/3/63/3242e2422c1917170dcbaae54534e.jpg',
    'https://s5o.ru/storage/dumpster/f/36/c37c15826439bc94d20f0fd848587.png'
  ]
}]

export const trends = [
  {
    name: '#GoLang',
    tweetsCount: 155614
  },
  {
    name: '#Python',
    tweetsCount: 121353
  },
  {
    name: '#DevConf2022',
    tweetsCount: 90420
  }
]