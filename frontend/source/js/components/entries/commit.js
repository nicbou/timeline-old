export default Vue.component('commit-entry', {
  props: ['entry'],
  computed: {
    filesChangedString: function() {
      if(this.entry.extra_attributes.changes.files === 1) {
        return `${this.entry.extra_attributes.changes.files} file changed`;
      }
      return `${this.entry.extra_attributes.changes.files} files changed`;
    }
  },
  template: `
    <div class="commit">
      <i class="icon fab fa-git-square" :title="new Date(entry.date_on_timeline).toLocaleString()"></i>
      <div class="meta">
        <a target="_blank" :href="entry.extra_attributes.url || entry.extra_attributes.repo.url">Commit</a> to <a target="_blank" :href="entry.extra_attributes.repo.url">{{ entry.extra_attributes.repo.name }}</a>
      </div>
      <div class="content">
        {{ entry.title }}
        <small>
          {{ filesChangedString }}
          (+{{ entry.extra_attributes.changes.insertions }}, -{{ entry.extra_attributes.changes.deletions }})
        </small>
      </div>
    </div>
  `
});