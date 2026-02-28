let template = `
<div class="patheditor">
  <span class="pathitem" @click="handle(-1)" style="font-weight: bold; color: #0066cc;">/ </span>
  <span v-for="(dir, index) in pathlist" class="pathitem" @click="handle(index)">
    {{dir}}/
  </span>
</div>
`

export const PathEditor = {
  name: "path-editor",
  props: ["pathlist"],
  data: () => ({}),
  methods: {
    handle(index) {
      // index = -1 means click on root, return empty pathlist
      if (index < 0) {
        this.$emit("change", []);
      } else {
        this.$emit("change", this.pathlist.slice(0, index+1));
      }
    }
  },
  template
}