export const baseOptions = {
  nav: {
    title: 'ZeroTrust Agents',
    url: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  },
  links: [
    {
      text: 'Back to Website',
      url: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
      active: 'nested-url',
    },
    // {
    //   text: 'App Console',
    //   url: `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/app`,
    // },
  ],
  githubUrl: 'https://github.com/lokeshsk/zerotrust-agents',
};
