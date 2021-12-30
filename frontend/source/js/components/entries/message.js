export default Vue.component('message-entry', {
  props: ['entry'],
  computed: {
    iconClass: function() {
      if (this.entry.schema.startsWith('message.text.sms')) {
        return 'fas fa-sms';
      }
      else if (this.entry.schema.startsWith('message.telegram')){
        return 'fab fa-telegram-plane';
      }
      else if (this.entry.schema.startsWith('message.facebook')){
        return 'fab fa-facebook-messenger';
      }
    },
    entryClass: function() {
      if (this.entry.schema.startsWith('message.text.sms')) {
        return 'sms';
      }
      else if (this.entry.schema.startsWith('message.telegram')){
        return 'telegram';
      }
      else if (this.entry.schema.startsWith('message.facebook')){
        return 'facebook-messenger';
      }
    },
    senderName: function() {
      return this.entry.extra_attributes.sender_name || this.entry.extra_attributes.sender_id;
    },
    recipientName: function() {
      return this.entry.extra_attributes.recipient_name || this.entry.extra_attributes.recipient_id;
    },
  },
  template: `
    <div :class="entryClass">
      <i class="icon" :class="iconClass"></i>
      <div class="meta">
        <span :title="senderName" class="sender">{{ senderName }}</span>
         ▸ 
        <span :title="recipientName" class="recipient">{{ recipientName }}</span>
      </div>
      <div class="content">
        <image-thumbnail
          v-if="entry.extra_attributes.file && entry.extra_attributes.file.mimetype.startsWith('image/') && entry.extra_attributes.previews"
          @select="$emit('select', entry)"
          :entry="entry"></image-thumbnail>
        <video-thumbnail
          v-if="entry.extra_attributes.file && entry.extra_attributes.file.mimetype.startsWith('video/') && entry.extra_attributes.previews"
          @select="$emit('select', entry)"
          :entry="entry"></video-thumbnail>
        <audio controls
          v-if="entry.extra_attributes.file && entry.extra_attributes.file.mimetype.startsWith('audio/')" :src="entry.extra_attributes.file.path"></audio>
        {{ entry.description }}
      </div>
    </div>
  `
});