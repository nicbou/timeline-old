export const filters = {
  blog: {
    displayName: 'blog post',
    displayNamePlural: 'blog posts',
    iconClass: 'fas fa-rss-square',
    filterFunction: (entry) => entry.schema.startsWith('social.blog.'),
  },
  browse: {
    displayName: 'page view',
    displayNamePlural: 'page views',
    iconClass: 'fas fa-globe-americas',
    filterFunction: (entry) => entry.schema.startsWith('activity.browsing'),
  },
  file: {
    displayName: 'file',
    displayNamePlural: 'files',
    iconClass: 'fas fa-file',
    filterFunction: (entry) => entry.schema.startsWith('file'),
  },
  image: {
    displayName: 'image',
    displayNamePlural: 'images',
    iconClass: 'fas fa-image',
    filterFunction: (entry) => entry.schema.startsWith('file.image'),
  },
  hackerNews: {
    displayName: 'Hacker News entry',
    displayNamePlural: 'Hacker News entries',
    iconClass: 'fab fa-y-combinator',
    filterFunction: (entry) => entry.schema.startsWith('social.hackernews'),
  },
  journal: {
    displayName: 'journal entry',
    displayNamePlural: 'journal entries',
    iconClass: 'fas fa-pen-square',
    filterFunction: (entry) => entry.schema === 'journal',
  },
  location: {
    displayName: 'location ping',
    displayNamePlural: 'location pings',
    iconClass: 'fas fa-map-marker-alt',
    filterFunction: (entry) => entry.extra_attributes.location && entry.extra_attributes.location.latitude && entry.extra_attributes.location.longitude,
  },
  message: {
    displayName: 'message',
    displayNamePlural: 'messages',
    iconClass: 'fas fa-comments',
    filterFunction: (entry) => entry.schema.startsWith('message'),
  },
  motion: {
    displayName: 'exercise session',
    displayNamePlural: 'exercise sessions',
    iconClass: 'fas fa-running',
    filterFunction: (entry) => entry.schema.startsWith('activity.exercise.session'),
  },
  reddit: {
    displayName: 'reddit entry',
    displayNamePlural: 'reddit entries',
    iconClass: 'fab fa-reddit',
    filterFunction: (entry) => entry.schema.startsWith('social.reddit.'),
  },
  transaction: {
    displayName: 'transaction',
    displayNamePlural: 'transactions',
    iconClass: 'fas fa-piggy-bank',
    filterFunction: (entry) => entry.schema === 'finance.income' || entry.schema === 'finance.expense',
  },
  twitter: {
    displayName: 'tweet',
    displayNamePlural: 'tweets',
    iconClass: 'fab fa-twitter',
    filterFunction: (entry) => entry.schema.startsWith('social.twitter.'),
  },
  video: {
    displayName: 'video',
    displayNamePlural: 'videos',
    iconClass: 'fas fa-video',
    filterFunction: (entry) => entry.schema.startsWith('file.video'),
  },
}