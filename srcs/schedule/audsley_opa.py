if __name__ == "__main__":    
    import os, sys
    sys.path.append(os.getcwd())
    print(sys.path)
    
from generator.dist import *

def audsley_opa(ts, m, schedtest):

    n = len(ts)

    sort_choices = [ts.sort_by_deadline, lambda : ts.sort_by_dkc(m), ts.sort_by_deadline_minus_cost]
    schedule_algo = uniform_choice(sort_choices)
    schedule_algo()
    # print("audsley_opa input ts=", ts)

    bScheduleable = True

    for k in range(n - 1, 0, -1):
        assigned = False
        j = k
        while (not assigned) and (j>=0):
            if schedtest(ts):
                #assigned task posistion k to priority k
                assigned = True
                break
            else:
                # swap the task at priority/position j and j-1
                j -= 1
                ts[k], ts[j] = ts[j], ts[k]
        if (j < 0):
            # print("zzz")
            bScheduleable = False
            break
    
    # print(bScheduleable )
    # print("audsley_opa ret {}, output ts=".format(bScheduleable, ts))
    return bScheduleable 
            

if __name__ == "__main__":    
    
    # from ... import model    
    from rtmodel import tasks
    from schedule import rta_lc_guan09 as rtalc
    
    m = 2

    ts = tasks.TaskSystem([
        #1
        # tasks.SporadicTask(1,  4),
        # tasks.SporadicTask(4,  5),            
        # tasks.SporadicTask(3,  9),
        # tasks.SporadicTask(9, 12),    

        #2
        # tasks.SporadicTask(28,  50),
        # tasks.SporadicTask(13,  30),            
        # tasks.SporadicTask(5,  50),
        # tasks.SporadicTask(6, 30),    
        # tasks.SporadicTask(6, 40),  

        #3
        # tasks.SporadicTask(4229,  5139),
        # tasks.SporadicTask(179,  329),            
        # tasks.SporadicTask(86,  512),
        # tasks.SporadicTask(1571, 6488),    
        # tasks.SporadicTask(37, 87),  

        #4
        # tasks.SporadicTask(24,  24),
        # tasks.SporadicTask(194,  1790),            
        # tasks.SporadicTask(18,  77),
        # tasks.SporadicTask(3, 10),    
        # tasks.SporadicTask(990, 1202),

        #5
        # tasks.SporadicTask(7612, 8656),
        # tasks.SporadicTask(243,  771),            
        # tasks.SporadicTask(245,  651),
        # tasks.SporadicTask(65, 89),    
        # tasks.SporadicTask(70, 431),

        #6
        tasks.SporadicTask(577, 927),
        tasks.SporadicTask(192, 2162),            
        tasks.SporadicTask(38,  92),
        tasks.SporadicTask(49,161),    
        tasks.SporadicTask(2453, 7298),

    ])

    ts.sort_by_deadline()
    # b = rtalc.is_schedulable_rta_lc(m, ts)
    # print("rta lc", b)
    # for t in ts:
    #     print  (t.cost,  t.deadline , t.response_time)

    for t in ts:
        t.response_time = 0

    print("total u=",ts.utilization())

    b = rtalc.is_schedulable_rta_lc(m, ts)
    print("c-rta lc", b)
    for t in ts:
        print  (t.cost,  t.deadline , t.response_time)

    exit(0)

    for t in ts:
        t.response_time = 0
    b = rtalc.is_schedulable_d_rta(m, ts)
    print("d-rta lc", b)
    for t in ts:
        print  (t.cost,  t.deadline , t.response_time)

    b = rtalc.is_schedulable_da_lc(m, ts)
    print("da-lc", b)
    exit(0)

    b = rtalc.is_schedulable_c_rta(m, ts)
    print("c-rta lc", b)
    b = rtalc.is_schedulable_d_rta(m, ts)
    print("d-rta lc", b)


    ts.sort_by_deadline()
    b = rtalc.is_schedulable_rta_lc(m, ts)
    print("rta lc", b)
    b = rtalc.is_schedulable_c_rta(m, ts)
    print("c-rta lc", b)

    b = rtalc.is_schedulable_d_rta(m, ts)
    print("d-rta lc", b)

    b = audsley_opa(ts, m, lambda x: rtalc.is_schedulable_da_lc(m, x))
    print ("audsley_opa", b, ts)

    

    # ts.sort_by_period()
    # # ts.sort_by_dkc(2)
    # print(ts)

    # # print rtalc.is_schedulable(1, ts)
    # # for t in ts:
    # #     print t.response_time, t.deadline 
    # print("is_schedulable_rta_lc")
    # print (rtalc.is_schedulable_rta_lc(2, ts))
 
