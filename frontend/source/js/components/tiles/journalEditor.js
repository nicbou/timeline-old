export default Vue.component('journal-editor', {
  data: function() {
    return {
      isEditing: false,
      asMarkdown: "",
    }
  },
  computed: {
    prettyDate: function() {
      return moment(this.$store.state.route.query.date, 'YYYY-MM-DD', true).format('LL');
    },
    journalEntryDescription: function() {
      const existingEntry = this.$store.state.timeline.entries.find(e => e.schema === 'journal');
      return existingEntry ? existingEntry.description : "";
    },
    asHtml: function() {
      if (this.journalEntryDescription) {
        return marked(this.journalEntryDescription);
      }
      return '<p class="placeholder">Write something</p>'
    },
  },
  methods: {
    editEntry: function() {
      this.asMarkdown = this.journalEntryDescription;
      this.isEditing = true;
      this.$nextTick(() => {
        this.$refs.editor.focus();
      });
    },
    saveChanges: function(){
      return this.$store.dispatch('timeline/setJournalEntry', this.asMarkdown);
    },
  },
  template: `
    <article class="post tile journal">
      <header>
        <span class="post-icon">
          <i class="fas fa-pen-square"></i>
        </span>
        <span class="post-title">
          {{ prettyDate }}
        </span>
      </header>
      <main>
        <textarea ref="editor" v-show="isEditing" v-model="asMarkdown" @change="saveChanges" @blur="isEditing = false"></textarea>
        <div v-html="asHtml"
          v-if="!isEditing"
          @click="editEntry"></div>
      </main>
    </article>
  `
});