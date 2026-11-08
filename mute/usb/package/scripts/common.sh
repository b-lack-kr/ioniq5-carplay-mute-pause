# Sourced by NEMESIS package hooks with the package root as cwd.
export PATH=/system/bin:/system/xbin:/data/nemesis/bin
umask 077
ID=neev-carplay-mute-pause
MOD=/data/hmgapi/mods/neev-carplay-mute-pause
H=/system/bin/hmgapid
UUID=@AUTHOR_UUID@

fail() { echo "CarPlay Mute Pause: $*" >&2; exit 1; }
hash_is() {
    [ -f "$1" ] && [ ! -L "$1" ] || return 1
    digest=$(md5 "$1") || return 1
    [ "${digest%% *}" = "$2" ]
}
verify_installed() {
    ( export CLASSPATH=/system/framework/hmgapi-hook.jar ANDROID_ROOT=/system ANDROID_DATA=/data
      unset HMGAPI_SELFTEST
      exec /system/bin/app_process /system/bin hmgapi.engine.Signing verify "$MOD" "$UUID" )
}
current_release() {
    [ -d "$MOD" ] && [ ! -L "$MOD" ] && [ ! -L "$MOD/META-HMGAPI" ] &&
        hash_is "$MOD/META-HMGAPI/manifest.json" @MOD_MANIFEST_MD5@ && verify_installed
}
installed_release() {
    [ -d "$MOD" ] && [ ! -L "$MOD" ] && [ ! -L "$MOD/META-HMGAPI" ] || return 1
    if ! hash_is "$MOD/META-HMGAPI/manifest.json" @MOD_MANIFEST_MD5@; then
        # Only our exact previously released 1.0.0 and 1.1.0 builds may be replaced.
        [ "$UUID" = "bd5f651c-38f9-8ef4-827c-34ad706c2b5c" ] || return 1
        hash_is "$MOD/META-HMGAPI/manifest.json" 3152f3e47803c0cdc6081b27015fd1ee ||
            hash_is "$MOD/META-HMGAPI/manifest.json" 90bfe998c4bcd2ec1dc173b31de5b73d ||
            hash_is "$MOD/META-HMGAPI/manifest.json" 668c07b58a8df5d72940a19245db4d3d || return 1
    fi
    verify_installed
}
has_installed() { [ -e "$MOD" ] || [ -L "$MOD" ]; }
hmg_version_supported() (
    # Accept exactly three canonical numeric components. Do not treat prerelease,
    # build suffixes, partial versions, or arbitrary command output as a release.
    case "$1" in 'hmgapid '*) version=${1#hmgapid } ;; *) return 1 ;; esac
    case "$version" in ''|*[!0-9.]*|.*|*.|*..*) return 1 ;; esac
    IFS=.
    set -f
    set -- $version
    [ "$#" = 3 ] || return 1
    for component do
        case "$component" in ''|*[!0-9]*|0[0-9]*) return 1 ;; esac
    done
    # Numeric >= 1.0.1 with canonical components, without integer overflow:
    # major 0 is older; major 1 needs a nonzero minor or patch; major >= 2 wins.
    case "$1" in
        0) return 1 ;;
        1) [ "$2" != 0 ] || [ "$3" != 0 ] ;;
        *) return 0 ;;
    esac
)
engine_ready() {
    engine_version=$("$H" version) || fail HMG_API_VERSION_READ_FAILED
    hmg_version_supported "$engine_version" || fail HMG_API_101_OR_NEWER_REQUIRED
    "$H" ping >/dev/null || fail HMG_API_NOT_RUNNING
    [ ! -e /data/hmgapi/state/journal.json ] || fail UNFINISHED_HMG_TRANSACTION
}
check_install() {
    [ "$(getprop ro.build.product)" = NEEV.KOR.0000.V039.001.260902 ] &&
        [ "$(getprop ro.board.platform)" = tcc803x ] || fail WRONG_HEAD_UNIT
    [ "$(getprop sys.boot_completed)" = 1 ] || fail WAIT_FOR_BOOT
    hash_is /system/app/HKMC_DiPO.odex 3b26cdcbf3c43f75623311f2bdfc3471 || fail WRONG_DIPO_BUILD
    [ ! -L mod ] && [ "$(cat mod/id)" = "$ID" ] && hash_is mod/package.zip @PACKAGE_ZIP_MD5@ || fail PACKAGE_MISMATCH
    engine_ready
    map=$("$H" engine map) || fail HOOK_MAP_READ_FAILED
    case "$map" in *'hooks on'*) ;; *) fail HOOK_MAP_DISABLED;; esac
    if has_installed; then installed_release || fail EXISTING_MOD_MISMATCH; fi
}
