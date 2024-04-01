def remove_prefix_suffix_and_slice(s):
    if not s.startswith("docker-"):
          return "error"
    else:
        s = s.replace("docker-", "")
        s = s.replace(".scope", "")
        return s[:12]


# 示例
# s =  "dockr-12f1ed1e40da04819e307f27c4cbaae519953cd695cdd169cc2b348961dc4ffc.scope"
#
# print(remove_prefix_suffix_and_slice(s))