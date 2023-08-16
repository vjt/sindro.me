---
title: The best way to begin a new day
date: 2009-05-26T10:00:00Z
tags: [data, linux, recovery, xfs]
categories: [development, all]
---

```
XFS internal error XFS_WANT_CORRUPTED_RETURN at line 295 of file fs/xfs/xfs_alloc.c.  Caller 0xc018066c
 [<c017fed0>] xfs_alloc_fixup_trees+0x1b0/0x2e0
 [<c018066c>] xfs_alloc_ag_vextent_near+0x31c/0x9c0
 [<c018066c>] xfs_alloc_ag_vextent_near+0x31c/0x9c0
 [<c0180187>] xfs_alloc_ag_vextent+0xf7/0x100
 [<c01824fe>] xfs_alloc_vextent+0x35e/0x420
 [<c019015d>] xfs_bmap_alloc+0x80d/0x12b0
 [<c0111254>] try_to_wake_up+0xa4/0xc0
 [<c02cf248>] schedule+0x308/0x5c0
 [<c01939c4>] xfs_bmapi+0x514/0x1470
 [<c0130069>] find_lock_page+0x29/0xe0
 [<c013013c>] find_or_create_page+0x1c/0xb0
 [<c01d9116>] kmem_zone_zalloc+0x26/0x50
 [<c01a2296>] xfs_dir2_grow_inode+0xf6/0x3c0
 [<c01b57a6>] xfs_iget_core+0x326/0x5a0
 [<c0163315>] alloc_inode+0xd5/0x170
 [<c01b978b>] xfs_idata_realloc+0x3b/0x160
 [<c01a3e2d>] xfs_dir2_sf_to_block+0xad/0x680
 [<c0137882>] cache_grow+0xe2/0x150
 [<c01aa27b>] xfs_dir2_sf_addname+0x9b/0x110
 [<c01a1c51>] xfs_dir2_createname+0x131/0x140
 [<c01d9116>] kmem_zone_zalloc+0x26/0x50
 [<c01cebcb>] xfs_trans_ijoin+0x2b/0x80
 [<c01d4967>] xfs_create+0x407/0x6c0
 [<c017e766>] xfs_acl_vhasacl_default+0x36/0x50
 [<c01df8f4>] linvfs_mknod+0x2c4/0x390
 [<c01a1d62>] xfs_dir2_lookup+0x102/0x110
 [<c01228b8>] in_group_p+0x38/0x70
 [<c01ba9a6>] xfs_iaccess+0xc6/0x1a0
 [<c0157cb7>] permission+0x97/0xd0
 [<c0158f94>] __link_path_walk+0xda4/0xe90
 [<c0157cb7>] permission+0x97/0xd0
 [<c015984c>] vfs_create+0x9c/0x120
 [<c015a00b>] open_namei+0x58b/0x5e0
 [<c014aa9d>] filp_open+0x2d/0x50
 [<c014ac70>] get_unused_fd+0x50/0xc0
 [<c0157ae7>] getname+0x67/0xb0
 [<c014ad9c>] sys_open+0x3c/0x80
 [<c0102867>] sysenter_past_esp+0x54/0x75

xfs_force_shutdown(hda8,0x8) called from line 1091 of file fs/xfs/xfs_trans.c.  Return address = 0xc01e2c5c
Filesystem "hda8": Corruption of in-memory data detected.  Shutting down filesystem: hda8
Please umount the filesystem, and rectify the problem(s)
xfs_force_shutdown(hda8,0x1) called from line 353 of file fs/xfs/xfs_rw.c.  Return address = 0xc01e2c5c
printk: 12 messages suppressed.
```

Yeah, I'd umount `/var`, if this box didn't `act_as_router` and didn't run `pppd` that didn't lock `/var/run/pppd2.tdb`...

```
pppd   222 root  mem   REG    3,8    88080525 /var/run/pppd2.tdb (path dev=0,0 inode=34)
```

Of course `kill 222 ; pppd call dsl-provider` doesn't work. **YUCK**. Let's put a router in front of it.. configure, portforward, and start over.. then `fdisk /dev/hdc` to recreate partitions structure on the new hard disk, `mkfs.xfs` on all the new partitions, `mount /dev/hdcX /target`, `pax -r -w -p e /{bin,boot,dev,etc,home,initrd,lib,media,root,sbin,srv,tmp,usr,var} /target`... wait a lot for the copy to complete because of damaged sectors on the source hard disk, `chroot /target`, `vi /etc/lilo.conf` and substitute `boot=/dev/hda` with `boot=/dev/hdc`, run `lilo -v` while in the chroot verify `/etc/fstab`, and finally `shutdown` to remove the faulty disk, and boot again.. restoring `lilo.conf`. yay!
