import { sourceTypes } from './../../services/source-service.js';
import SpinnerComponent from '../spinner.js'

export default Vue.component('source-trakt', {
  props: ['source', 'isNew'],
  data: function() {
    return {
      isLoading: false,
      authInfo: null,
      authStatus: false,
      authPin: null,
    }
  },
  methods: {
    startPoll: function() {
      // GET request to backend to start polling
      // Receive a code to visit in response
      this.isLoading = true
      fetch(this.source.url + 'start_poll/')
            .then(response => response.json())
            .then(data => this.authInfo = { url: data.verification_url, code: data.user_code })
            .finally(this.isLoading = false);
    },
    checkAuthStatus: function() {
      // Queries the OAuth endpoint to see if the details are ok
      this.isLoading = true
      fetch(this.source.url + 'status/')
      .then(response => response.json())
      .then(data => this.authStatus = data.status)
      .finally(this.isLoading = false);
    },  
    getURL: function() {
      // Obtain URL for obtaining pin. 1st stage of OAuth process
      this.isLoading = true
      fetch(this.source.url + 'get_url/')
            .then(response => response.json())
            .then(data => this.authInfo = { url: data.url })
            .finally(this.isLoading = false);
    },
  },
  computed: {
    display_status: function() {
      // Prettify the authentication status message
      if (this.authStatus){
        return 'Connected \u{2705}';
      }
      else {
        return 'False \u{274C}';
      }
    },
    submitPin: function() {
      this.isLoading = true
      fetch(this.source.url + 'put_pin/',{
        method: 'PUT',
        headers:{
          'Content-Type':'application/json'
        },        
        body: JSON.stringify({'pin': this.authPin})
      })
            .then(this.authStatus = true)
            .finally(this.isLoading = false);
      this.checkAuthStatus()
    }

  },
  mounted: function() {
    this.checkAuthStatus()
  },
  template: `
    <div>
      <h3>Authentication Status: {{ display_status }} </h3>
      <spinner v-if="isLoading"></spinner>
      <button v-on:click="checkAuthStatus">Refresh Status</button>
      <template v-if="!authStatus">
          <button v-on:click="getURL">Authenticate</button>
          <div v-if="authInfo">
            <p>Please visit <a :href="authInfo.url">{{ authInfo.url }}</a></p>
            <input v-model="authPin" placeholder="Paste response code here">
            <button v-on:click="submitPin">Submit</button>
          </div>
      </template>
    </div>
    `
});