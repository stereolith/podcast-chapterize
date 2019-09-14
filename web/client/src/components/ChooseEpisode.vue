<template>
  <div class="flex flex-col">
    <div class="flex flex-col mb-5">
      <div class="flex flex-row items-center justify-center border-bottom my-4">
        <div class="h-10 w-10 rounded-full flex items-center justify-center bg-gray-200 text-xl mr-2">1</div>
        <h2 class="text-lg text-center">Enter a podcast RSS feed URL</h2>
      </div>
      <div class="flex flex-row">
        <input type="text" v-model="feedUrl" placeholder="feed URL" :class="{'bg-red-200 border-red-200': urlError}" class="flex-1 border border-gray-600 text-gray-700 focus:border-pink-400 py-3 px-4"/>
      </div>
      <div class="text-red-600" v-if="urlError">No podcast feed was forund for this URL.</div>
      <div v-if="loading" class="lds-ellipsis self-center"><div></div><div></div><div></div><div></div></div>
    </div>


    <div v-if="episodesFound" class="flex flex-col mb-5">
      <div class="flex flex-row items-center justify-center border-bottom my-4">
        <div class="h-10 w-10 rounded-full flex items-center justify-center bg-gray-200 text-xl mr-2">2</div>
        <h2 class="text-lg text-center">Choose language</h2>
      </div>
      <div v-if="languageDetected" class="self-center mb-3 text-pink-500">{{languages[selectedLanguage].label}} detected!</div>
      <div v-if="unsupportedLanguage" class="self-center my-3">The detected language is not supported.</div>
      <field-select
        :values="languages.map((lang) => lang.label)"
        :active-value="selectedLanguage"
        @changeLang="lang => { selectedLanguage = lang; languageDetected = false}"
      />
    </div>


    <div v-if="episodesFound && selectedLanguage != null" class="flex flex-col">
      <div class="flex flex-row items-center justify-center border-bottom my-4 mt-6">
        <div class="h-10 w-10 rounded-full flex items-center justify-center bg-gray-200 text-xl mr-2">3</div>
        <h2 class="text-lg text-center">Choose an episode</h2>
      </div>
      <select 
        v-model="selectedEpisode"
        name="episode"
        id="episodeSelect"
        class="block appearance-none w-full border border-gray-600 text-gray-700 py-3 px-4 pr-8 bg-white focus:border-pink-400 focus:outline-none focus:border-gray-500">
        <option
          v-for="episode in episodes"
          :value="episode.index"
          :key="episode.index"
        >
          {{episode.label}}
        </option>
      </select>
    </div>
    <button
      v-if="episodesFound && !jobStarted"
      @click="startJob"
      class="px-4 py-2 mt-8 bg-pink-400 hover:bg-pink-500 rounded text-white font-bold w-1/3 self-center"
      :class="{'bg-gray-400 cursor-not-allowed': jobStarted}"
    >Start chapterize episode</button> 
    <div v-if="postError">There was an error when trying to start the chapterization.</div>
  </div>
</template>

<script>
import { postJob, getEpisodes, getLanguage } from "../resources"

import FieldSelect from "../elements/FieldSelect"

export default {
  name: 'ChooseEpisode',
  components: {
    FieldSelect
  },
  data () {
    return {
      feedUrl: '',
      loading: false,
      languages: [
        {code: 'en', label: 'English'},
        {code: 'de', label: 'German'}
      ],
      languageDetected: false,
      selectedLanguage: null,
      unsupportedLanguage: false,
      episodesFound: false,
      episodes: [],
      selectedEpisode: 0,
      urlError: false,
      jobStarted: false,
      postError: false
    }
  },
  methods: {
    fetchLanguage () {
      this.loading = true
      getLanguage(this.feedUrl).then((res) => {
        this.loading = false
        if (res.data.language === 'en' || res.data.language === 'de') {
          this.languageDetected = true
          this.selectedLanguage = res.data.language === 'en' ? 0 : 1
        } else {
          this.unsupportedLanguage = true
        }
      })
      .catch((error) => {
        this.loading = false
      })
    },
    fetchEpisodes () {
      this.loading = true

      getEpisodes(this.feedUrl).then((res) => {
        this.loading = false
        this.urlError = false
        this.episodesFound = true
        this.episodes = res.data.episodes
      })
      .catch((error) => {
        this.loading = false
        this.episodesFound = false
        this.urlError = true
        console.error(error)
      });
    },
    startJob () {
      postJob(this.feedUrl, this.selectedEpisode, this.languages[this.selectedLanguage].code).then((res) => {
        this.loading = false
        this.urlError = false
        this.episodesFound = true
        this.$store.commit('setStep', 'JOB RUNNING')
        this.$store.commit('setId', res.data.jobId)
        this.$store.dispatch('updateStatus')
      })
      .catch((error) => {
        this.postError = true
        console.error(error)
      });
    }
  },
  watch: {
    feedUrl () {
      this.fetchLanguage()
      this.fetchEpisodes()
    },
    selectedLanguage (val) {
      if (val && !this.episodesFound) this.fetchEpisodes()
    }
  },
  mounted() {
    //this.fetchEpisodes()
  }
}
</script>


<style>
.lds-ellipsis {
  display: inline-block;
  position: relative;
  width: 64px;
  height: 64px;
}
.lds-ellipsis div {
  position: absolute;
  top: 27px;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: #4a5568;
  animation-timing-function: cubic-bezier(0, 1, 1, 0);
}
.lds-ellipsis div:nth-child(1) {
  left: 6px;
  animation: lds-ellipsis1 0.6s infinite;
}
.lds-ellipsis div:nth-child(2) {
  left: 6px;
  animation: lds-ellipsis2 0.6s infinite;
}
.lds-ellipsis div:nth-child(3) {
  left: 26px;
  animation: lds-ellipsis2 0.6s infinite;
}
.lds-ellipsis div:nth-child(4) {
  left: 45px;
  animation: lds-ellipsis3 0.6s infinite;
}
@keyframes lds-ellipsis1 {
  0% {
    transform: scale(0);
  }
  100% {
    transform: scale(1);
  }
}
@keyframes lds-ellipsis3 {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(0);
  }
}
@keyframes lds-ellipsis2 {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(19px, 0);
  }
}

</style>
