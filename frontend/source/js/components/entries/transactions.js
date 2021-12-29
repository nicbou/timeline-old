export default Vue.component('transactions-entry', {
  props: ['entries'],
  computed: {
    transactions: function(){
      return this.entries.map(entry => {
        let transaction = {};
        const isExpense = entry.extra_attributes['sender_name'] === null;
        if (isExpense) {
          transaction = {
            type: 'expense',
            amount: Number(entry.extra_attributes['sender_amount'] * -1).toFixed(2),
            otherCurrency: entry.extra_attributes['recipient_currency'],
            otherCurrencyAmount: Number(entry.extra_attributes['recipient_amount']).toFixed(2),
            otherPartyName: entry.extra_attributes['recipient_name'],
          }
        }
        else {
          transaction = {
            type: 'income',
            amount: Number(entry.extra_attributes['recipient_amount']).toFixed(2),
            otherCurrency: entry.extra_attributes['sender_currency'],
            otherCurrencyAmount: Number(entry.extra_attributes['sender_amount']).toFixed(2),
            otherPartyName: entry.extra_attributes['sender_name'],
          }
        }

        if (entry.description){
          transaction.description = `${entry.title} - ${entry.description}`;
        }
        else {
          transaction.description = entry.title;
        }
        return transaction;
      })
    }
  },
  template: `
    <article class="post transactions" v-if="transactions.length">
      <header>
        <span class="post-icon">
          <i class="fas fa-piggy-bank"></i>
        </span>
        Transactions
      </header>
      <main>
        <table>
          <tbody>
            <tr v-for="transaction in transactions">
              <td>
                <strong>{{ transaction.otherPartyName }}</strong>
                <small>{{ transaction.description }}</small>
              </td>
              <td class="currency">{{ transaction.amount }} €</td>
            </tr>
          </tbody>
        </table>
      </main>
    </article>
  `
});