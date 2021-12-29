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
    },
    messageClass: function() {
      if (this.entry.schema.startsWith('message.text.sms')) {
        return 'sms';
      }
      else if (this.entry.schema.startsWith('message.telegram')){
        return 'telegram';
      }
    },
    time: function() {
      return moment(this.entry.date_on_timeline).format('HH:mm');
    },
    senderName: function() {
      return this.entry.extra_attributes.sender_name || this.entry.extra_attributes.sender_id;
    },
    recipientName: function() {
      return this.entry.extra_attributes.recipient_name || this.entry.extra_attributes.recipient_id;
    },
  },
  template: `
    <div class="message compact" :class="messageClass">
      <header>
        <i class="icon" :class="iconClass"></i>
        <time>{{ time }}</time>
        <span class="participants">
          <span :title="senderName" class="sender">{{ senderName }}</span>
           ▸ 
          <span :title="recipientName" class="recipient">{{ recipientName }}</span></span>
      </header>
      <main>
        <image-entry
          v-if="entry.extra_attributes.file && entry.extra_attributes.file.mimetype.startsWith('image/') && entry.extra_attributes.previews"
          @select="$emit('select', entry)"
          :entry="entry"></image-entry>
        <video-entry
          v-if="entry.extra_attributes.file && entry.extra_attributes.file.mimetype.startsWith('video/') && entry.extra_attributes.previews"
          @select="$emit('select', entry)"
          :entry="entry"></video-entry>
        <audio controls
          v-if="entry.extra_attributes.file && entry.extra_attributes.file.mimetype.startsWith('audio/')" :src="entry.extra_attributes.file.path"></audio>
        {{ entry.description }}
      </main>
    </div>
  `
});