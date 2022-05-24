import TimelineEntryIcon from './entry-icon.js';

const postTypes = {
  twitter: {
    getIconClass: entry => 'fab fa-twitter',
    getUser: entry => `@${entry.extra_attributes.post_user}`,
    getUserUrl: entry => `https://twitter.com/${entry.extra_attributes.post_user}`,
    getPostUrl: entry => `https://twitter.com/${entry.extra_attributes.post_user}/status/${entry.extra_attributes.post_id}`,
    getPostWebsite: entry => 'Twitter',
    getPostCommunity: entry => null,
    getPostCommunityUrl: entry => null,
    getPostType: entry => 'Tweet',
    getRichDescription: entry => `<p>${entry.description}</p>`.replace(/@([\w]{1,50})/ig, '<a target="_blank" href="https://twitter.com/$1">@$1</a>'),
  },
  reddit: {
    getIconClass: entry => 'fab fa-reddit',
    getUser: entry => entry.extra_attributes.post_user,
    getUserUrl: entry => `https://reddit.com/user/${entry.extra_attributes.post_user}`,
    getPostUrl: entry => `https://reddit.com/comments/${entry.extra_attributes.post_thread_id}/_/${entry.extra_attributes.post_id}`,
    getPostWebsite: entry => 'Reddit',
    getPostCommunity: entry => `/r/${entry.extra_attributes.post_community}`,
    getPostCommunityUrl: entry => `https://www.reddit.com/r/${entry.extra_attributes.post_community}`,
    getPostType: entry => entry.schema === 'social.reddit.comment' ? 'Comment' : 'Post',
    getRichDescription: entry => {
      if(entry.schema === 'social.reddit.post') {
        return `<h3><a href="${entry.extra_attributes.post_url}">${entry.title}</a></h3>`;
      }
      return entry.extra_attributes.post_body_html;
    },
  },
  hackernews: {
    getIconClass: entry => 'fab fa-y-combinator',
    getUser: entry => entry.extra_attributes.post_user,
    getUserUrl: entry => `https://news.ycombinator.com/submitted?id=${entry.extra_attributes.post_user}`,
    getPostUrl: entry => `https://news.ycombinator.com/item?id=${entry.extra_attributes.post_id}`,
    getPostWebsite: entry => 'Hacker News',
    getPostCommunity: entry => null,
    getPostCommunityUrl: entry => null,
    getPostType: entry => entry.schema === 'social.hackernews.comment' ? 'Comment' : 'Submission',
    getRichDescription: entry => {
      if(entry.schema === 'social.hackernews.story'){
        return `<h3><a href="https://news.ycombinator.com/item?id=${entry.extra_attributes.post_id}">${entry.title}</a></h3>`
      }
      else {
        // The first paragraph isn't wrapped in a <p> tag
        return '<p>' + entry.extra_attributes.post_body_html.replace('<p>', '</p><p>');
      }
    },
  },
  blog: {
    getIconClass: entry => 'fas fa-rss',
    getUser: entry => entry.extra_attributes.post_user,
    getUserUrl: entry => null,
    getPostUrl: entry => entry.extra_attributes.post_url,
    getPostWebsite: entry => 'Website',
    getPostCommunity: entry => new URL(entry.extra_attributes.post_url).hostname,
    getPostCommunityUrl: entry => new URL(entry.extra_attributes.post_url).hostname,
    getPostType: entry => 'Post',
    getRichDescription: entry => entry.extra_attributes.post_body_html,
  },
}

export default Vue.component('post-entry', {
  props: ['entry'],
  computed: {
    postClass: function() {
      return this.entry.schema.split('.')[1];
    },
    postType: function() {
      return postTypes[this.postClass];
    },
  },
  template: `
    <div :class="postClass">
      <entry-icon :icon-class="postType.getIconClass(entry)" :entry="entry"></entry-icon>
      <div class="meta">
        <a :href="postType.getPostUrl(entry)" class="user" target="_blank">{{ postType.getPostType(entry) }}</a>
        <span v-if="postType.getPostCommunity(entry)">
          on <a :href="postType.getPostCommunityUrl(entry)" class="community" target="_blank">{{ postType.getPostCommunity(entry) }}</a>
        </span>
        <span v-if="!postType.getPostCommunity(entry)">
          on <a :href="postType.getPostUrl(entry)" class="community" target="_blank">{{ postType.getPostWebsite(entry) }}</a>
        </span>
        <span v-if="entry.extra_attributes.post_score !== undefined && entry.extra_attributes.post_score !== null" class="score" :class="{positive: entry.extra_attributes.post_score >= 1, negative: entry.extra_attributes.post_score < 1}">{{ entry.extra_attributes.post_score }}</span>
      </div>
      <div class="content" v-html="postType.getRichDescription(entry)"></div>
    </div>
  `
});