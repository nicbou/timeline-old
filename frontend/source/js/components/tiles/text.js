export default Vue.component('text-tile', {
  props: ['entry'],
  computed: {
    fileName: function() {
      const pathParts = this.entry.extra_attributes.path.split('/');
      return pathParts[pathParts.length - 1];
    },
  },
  template: `
    <article class="post text">
      <header>
        <a :href="postPermalink" class="post-icon" target="_blank">
          <i class="fas fa-file-alt"></i>
        </a>
        <span class="post-title">
          {{ fileName }}
        </span>
      </header>
      <main>
        {{ entry.description }}
      </main>
    </article>
  `
});