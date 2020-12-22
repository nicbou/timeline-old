export default Vue.component('text-preview', {
  props: ['entry'],
  template: `
    <text-tile :entry="entry"></text-tile>
  `
});