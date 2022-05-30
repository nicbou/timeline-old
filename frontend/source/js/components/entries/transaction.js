import TimelineEntryIcon from './entry-icon.js';

export default Vue.component('transaction-entry', {
  props: ['entry'],
  computed: {
    isExpense: function(){
      return this.entry.schema === 'finance.expense';
    },
    transactionType: function(){
      return this.isExpense ? 'expense' : 'income';
    },
    amount: function(){
      let amount = this.entry.extra_attributes.recipient.amount;
      if(this.isExpense) {
        amount = this.entry.extra_attributes.sender.amount;
      }
      return Number(amount).toFixed(2);
    },
    otherCurrencyAmount: function(){
      let amount = this.entry.extra_attributes.sender.amount;
      if(this.isExpense) {
        amount = this.entry.extra_attributes.recipient.amount;
      }
      return Number(amount).toFixed(2);
    },
    currency: function(){
      let currency = this.entry.extra_attributes.recipient.currency;
      if(this.isExpense) {
        currency = this.entry.extra_attributes.sender.currency;
      }
      return currency === 'EUR' ? '€' : currency;
    },
    otherCurrency: function(){
      let currency = this.entry.extra_attributes.sender.currency;
      if(this.isExpense) {
        currency = this.entry.extra_attributes.recipient.currency;
      }
      return currency === 'EUR' ? '€' : currency;
    },
    otherPartyName: function(){
      if(this.isExpense) {
        return this.entry.extra_attributes.recipient.name;
      }
      return this.entry.extra_attributes.sender.name;
    },
  },
  template: `
    <div class="transaction">
      <entry-icon icon-class="fas fa-piggy-bank" :entry="entry"></entry-icon>
      <div class="meta">{{ otherPartyName }}</div>
      <div class="content">
        <strong>{{ amount }}{{ currency }}</strong> {{ transactionType }}
        <span v-if="otherCurrency !== currency">({{ otherCurrencyAmount }}{{ otherCurrency }})</span>
        <small v-if="entry.description">{{ entry.description }}</small>
      </div>
    </div>
  `
});