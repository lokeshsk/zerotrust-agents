export const baseOptions = {
  nav: {
    title: 'ZeroTrust Agents',
  },
  links: [
    {
      text: 'Back to Website',
      url: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
    },
    {
      text: 'App Console',
      url: `${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/app`,
    },
    {
      text: 'GitHub',
      url: 'https://github.com/lokeshsk/zerotrust-agents',
    },
  ],
};
