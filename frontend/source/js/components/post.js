export default Vue.component('post', {
  props: ['entry'],
  computed: {
    postType: function() {
      return this.entry.schema.split('.')[1];
    },
    userPermalink: function() {
      if(this.postType === 'twitter') {
        return `https://twitter.com/${this.entry.extra_attributes.post_user}`;
      }
      else if(this.postType === 'reddit') {
        return `https://reddit.com/user/${this.entry.extra_attributes.post_user}`;
      }
    },
    userName: function() {
      if(this.postType === 'twitter') {
        return `@${this.entry.extra_attributes.post_user}`;
      }
      return this.entry.extra_attributes.post_user;
    },
    postPermalink: function() {
      if(this.postType === 'twitter') {
        return `${this.userPermalink}/status/${this.entry.extra_attributes.post_id}`;
      }
      else if(this.postType === 'reddit') {
        return `https://www.reddit.com/r/${this.entry.extra_attributes.post_community}/comments/${this.entry.extra_attributes.post_thread_id}/a/${this.entry.extra_attributes.post_id}/?context=3`;
      }
    },
    postScore: function() {
      return this.entry.extra_attributes.post_score;
    },
    postCommunity: function() {
      return this.entry.extra_attributes.post_community;
    },
    postCommunityUrl: function() {
      if(this.postType === 'reddit') {
        return `https://www.reddit.com/r/${this.entry.extra_attributes.post_community}`;
      }
      return null;
    },
    iconClass: function() {
      return `fa-${this.postType}`;
    },
    richDescription: function() {
      if(this.entry.schema === 'social.reddit.post') {
        return `<h3><a href="${this.entry.extra_attributes.post_url}">${this.entry.title}</a></h3>`;
      }
      return this.entry.extra_attributes.post_body_html || this.entry.description
        .replace(/@([\w]{1,50})/ig, '<a target="_blank" href="https://twitter.com/$1">@$1</a>')
        .replace(/\/r\/([\w]{1,20})/ig, '<a target="_blank" href="https://reddit.com/r/$1">@$1</a>')
        .replace(/\/u\/([\w]{1,20})/ig, '<a target="_blank" href="https://reddit.com/user/$1">@$1</a>');
    },
  },
  template: `
    <article :class="postType">
      <header>
        <a :href="postPermalink" class="post-icon" target="_blank">
          <i class="fab" :class="iconClass"></i>
        </a>
        <span class="post-title">
          <a :href="userPermalink" class="post-user">{{ userName }}</a>
          <span v-if="postCommunity">
            in <a v-if :href="postCommunityUrl" class="post-community">{{ postCommunity }}</a>
          </span>
        </span>
        <span v-if="postScore" class="post-score" :class="{positive: postScore >= 1, negative: postScore < 1}">{{ postScore }}</span>
      </header>
      <main>
        <p v-html="richDescription"></p>
      </main>

    </article>
  `
});