export default Vue.component('transaction-entry', {
  props: ['entry'],
  computed: {
    isExpense: function(){
      return this.entry.extra_attributes['sender_name'] === null;
    },
    transactionType: function(){
      return this.isExpense ? 'expense' : 'income';
    },
    amount: function(){
      let amount = this.entry.extra_attributes['recipient_amount'];
      if(this.isExpense) {
        amount = this.entry.extra_attributes['sender_amount'];
      }
      return Number(amount).toFixed(2);
    },
    otherCurrencyAmount: function(){
      let amount = this.entry.extra_attributes['sender_amount'];
      if(this.isExpense) {
        amount = this.entry.extra_attributes['recipient_amount'];
      }
      return Number(amount).toFixed(2);
    },
    currency: function(){
      let currency = this.entry.extra_attributes['recipient_currency'];
      if(this.isExpense) {
        currency = this.entry.extra_attributes['sender_currency'];
      }
      return currency === 'EUR' ? '€' : currency;
    },
    otherCurrency: function(){
      let currency = this.entry.extra_attributes['sender_currency'];
      if(this.isExpense) {
        currency = this.entry.extra_attributes['recipient_currency'];
      }
      return currency === 'EUR' ? '€' : currency;
    },
    otherPartyName: function(){
      if(this.isExpense) {
        return this.entry.extra_attributes['recipient_name'];
      }
      return this.entry.extra_attributes['sender_name'];
    },
  },
  template: `
    <div class="transaction">
      <i class="icon fas fa-piggy-bank" :title="new Date(entry.date_on_timeline).toLocaleString()"></i>
      <div class="meta">{{ otherPartyName }}</div>
      <div class="content">
        <strong>{{ amount }}{{ currency }}</strong> {{ transactionType }}
        <span v-if="otherCurrency !== currency">({{ otherCurrencyAmount }}{{ otherCurrency }})</span>
        <small v-if="entry.description">{{ entry.description }}</small>
      </div>
    </div>
  `
});