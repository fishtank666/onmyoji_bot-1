import os

import cv2
import numpy as np

from explore.explore_fight import ExploreFight
import tools.utilities as ut
from tools.game_pos import CommonPos, TansuoPos

import configparser
import logging
import random
import time
from gameLib.find_moster import FindMoster


class DriverExplore(ExploreFight):

    def __init__(self, hwnd=0):
        # 初始化
        ExploreFight.__init__(self, 'Driver: ', hwnd)

        self.find_moser = FindMoster()

        self.isDriver = True
        self.exp_templates = [
            'img/EXP.png',
            'img/EXP2.png',
            'img/EXP-XP.png',
        ]
        self.fuben_max_width = 2100
        self.now_fuben_width = 0

        self.gouliang1 = False
        self.gouliang2 = False
        self.gouliang3 = False

    def start(self):
        """
        开始战斗
        :return:
        """
        while self.run:
            logging.info(self.name + "正在检测当前场景")

            if self.yys.find_game_img('img/JI-XU.png'):
                self.click_until('继续邀请队友', 'img/JI-XU.png',
                                 *TansuoPos.ji_xu_btn, 0.7, False)

            # 开始检测当前战斗情况
            is_start, is_team, is_tansuo, is_juexing, is_yaoqing = self.check_now_scene()
            if not is_start and not is_team and not is_tansuo and not is_juexing and not is_yaoqing:
                self.log.writeinfo("等待进入场景")
                continue

            if is_juexing and is_yaoqing:
                continue

            if is_juexing and not is_yaoqing and not is_tansuo and not is_start:
                self.log.writeinfo('开始检测场景')
                # 检测场景
                self.yys.wait_game_img('img/JI-XU.png')

                self.click_until('继续邀请队友', 'img/JI-XU.png',
                                 *TansuoPos.ji_xu_btn,  0.7, False)
                continue
            if is_tansuo or is_team:
                self.log.writeinfo(self.name + ' 进入探索页面')

                # 开始查找经验怪
                self.find_exp_moster1()

    def fight_monster(self, pos1, pos2, boss=False):
        """
        挑战怪物
        :return:
        """
        # 要挑战位置
        pos_start = (pos1[0] - 100, pos1[1] - 50)
        pos_end = (pos2[0] + 100, pos2[1] + 200)
        img_src = self.yys.window_part_shot(pos_start, pos_end)
        cv2.imwrite('Temp/' + str(time.time()) + '.png', img_src)
        # print("要挑战怪物图")
        cv2.imshow("image", img_src)
        cv2.waitKey(0)
        templates = [
            'img/FIGHT.png'
        ]
        if boss:
            templates.append('img/BOSS.png')
        res = self.yys.find_img_from_src(img_src, *templates)
        if not res:
            time.sleep(1)
            return False
        pos1 = (res[0] + pos_start[0], res[1] + pos_start[1])
        pos2 = (pos1[0] + 15, pos1[1] + 10)
        self.click_until('挑战怪物', 'img/ZHUN-BEI.png', pos1, pos2, 0.8, True)

        self.wait_game_end()

        return True

    def find_exp_moster1(self):
        """
        查找经验怪物进行挑战
        """
        # pos1 = (2, 120)
        # pos2 = (1127, 600)

        # 战斗次数
        fight_num = 0
        self.log.writeinfo(self.name + '正在寻找怪物')

        while self.run and not self.fuben_is_end():
            times = 0
            while times <= 6:
                moster = []
                # 获取屏幕截图
                self.log.writeinfo(self.name + ' 获取屏幕截图')
                times += 1
                img_src = self.yys.window_full_shot()

                # 查找怪物
                guai = []
                img_template = cv2.imread('img/FIGHT.png')
                res = cv2.matchTemplate(img_src, img_template, cv2.TM_CCOEFF_NORMED)
                threshold = 0.8

                h, w = img_template.shape[:2]

                loc = np.where(res >= threshold)  # 匹配程度大于%80的坐标y,x
                n, ex, ey = 1, 0, 0
                for pt in zip(*loc[::-1]):  # *号表示可选参数
                    # 去掉相邻的点
                    x, y = pt[0] + int(w / 2) , pt[1] + int(h / 2)
                    if (x - ex) + (y - ey) < 15:
                        continue
                    ex, ey = x, y
                    guai.append([x, y])
                #     right_bottom = (pt[0] + w, pt[1] + h)
                #     cv2.rectangle(img_src, pt, right_bottom, (0, 0, 255), 2)
                # cv2.imshow("image", img_src)
                # cv2.waitKey(0)

                # 查找怪物是否是经验怪
                for item in guai:
                    print(item)
                    x0 = item[0] - 100
                    y0 = item[1] - 60
                    x1 = item[0] + 100
                    y1 = item[1] + 200

                    new_img = img_src[y0:y1, x0:x1]

                    # 区域查找 是否有经验图片
                    exp_pos = []
                    for template in self.exp_templates:
                        img_template = cv2.imread(template)
                        res = cv2.matchTemplate(new_img, img_template, cv2.TM_CCOEFF_NORMED)
                        threshold = 0.70
                        h, w = img_template.shape[:2]
                        loc = np.where(res >= threshold)  # 匹配程度大于%80的坐标y,x
                        n, ex, ey = 1, 0, 0
                        for pt in zip(*loc[::-1]):  # *号表示可选参数
                            # 去掉相邻的点
                            x, y = pt[0] + int(w / 2) , pt[1] + int(h / 2)
                            if (x - ex) + (y - ey) < 15:
                                continue
                            ex, ey = x, y
                            exp_pos.append([x, y])
                        #     right_bottom = (pt[0] + w, pt[1] + h)
                        #     cv2.rectangle(new_img, pt, right_bottom, (0, 0, 255), 2)
                        # cv2.imshow("image", new_img)
                        # cv2.waitKey(0)

                    for pos in exp_pos:
                        new_posy = y0 + pos[1]
                        if new_posy > item[1] and new_posy - 70 > item[1]:
                            fight_num += 1
                            self.fight_monster(item, (item[0] + 30, item[1] + 20))
                    break
                times += 1
                time.sleep(0.6)

            # 没有怪物，拖动场景
            times = 0
            self.log.writeinfo("拖动场景")
            self.next_scene()

        # 没有找到怪物 但是有经验怪 挑战BOSS
        is_fight_boss = False
        bossLoc = self.yys.find_game_img('img/BOSS.png')
        if bossLoc:
            print("挑战BOSS")
            is_fight_boss = True
            self.fight_monster(bossLoc, (bossLoc[0] + 50, bossLoc[1] + 40), True)

        if fight_num <= 0:
            # 随机选择一个怪物进行挑战
            maxLoc = self.yys.find_game_img('img/FIGHT.png')
            if maxLoc:
                self.fight_monster(maxLoc, (maxLoc[0] + 15, maxLoc[1] + 10))

        self.log.writeinfo('战斗结束 检测当前场景')
        # 开始检测当前战斗情况
        is_start, is_team, is_tansuo, is_juexing, is_yaoqing = self.check_now_scene()

        self.now_fuben_width = 0
        if is_tansuo and is_fight_boss:
            # 领取奖励
            self.receive_reward()

        if is_tansuo and not is_fight_boss:
            self.log.writeinfo('探索中 退出探索进行下一轮')
            self.quit_tansuo()

    def search_pos_exp_moster(self, pos1, pos2, sleep=3.5):
        """
        查找制定位置的经验怪
        :param pos1:
        :param pos2:
        :param sleep:
        :return: 经验怪位置
        """
        start = time.time()
        # 怪物坐标
        moster = []
        # 循环截图分析
        times = 0
        while self.run and time.time() - start <= sleep:
            img_src = self.yys.window_part_shot(pos1, pos2)
            times += 1
            for item in self.exp_templates:
                img_template = cv2.imread(item)

                res = cv2.matchTemplate(img_src, img_template, cv2.TM_CCOEFF_NORMED)
                threshold = 0.65

                h, w = img_template.shape[:2]

                loc = np.where(res >= threshold)  # 匹配程度大于%80的坐标y,x
                n, ex, ey = 1, 0, 0
                for pt in zip(*loc[::-1]):  # *号表示可选参数
                    # 去掉相邻的点
                    x, y = pt[0] + int(w / 2) + pos1[0], pt[1] + int(h / 2) + pos1[1]
                    if (x - ex) + (y - ey) < 15:
                        continue
                    ex, ey = x, y
                    moster.append([x, y])
                #     right_bottom = (pt[0] + w, pt[1] + h)
                #     cv2.rectangle(img_src, pt, right_bottom, (0, 0, 255), 2)
                # cv2.imshow("image", img_src)
                # cv2.waitKey(0)

            time.sleep(0.4)

        print("识别次数", times)
        # 识别完毕，开始整理boss 位置
        new_pos = []
        n, ex, ey = 1, 0, 0
        for pos in moster:
            x, y = pos[0] + 6, pos[1] + 6
            # 高度相差10的忽略
            if (y - ey) < 10 and (x - ex) < 85:
                continue

            ex, ey = x, y
            new_pos.append([x, y])
        return new_pos

    def next_scene(self, width=400):
        '''
        移动至下一个场景，每次移动400像素
        '''
        if width > 0:
            x0 = random.randint(width + 10, 1126)
            x1 = x0 - width
        else:
            x0 = random.randint(10, abs(width) - 10)
            x1 = x0 + abs(width)

        y0 = random.randint(210, 310)
        y1 = random.randint(210, 310)
        self.now_fuben_width += width
        print(self.now_fuben_width)
        self.yys.mouse_drag_bg((x0, y0), (x1, y1))

    def fuben_is_end(self):
        return self.now_fuben_width >= self.fuben_max_width
